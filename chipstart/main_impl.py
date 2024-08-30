import asyncio
import coloredlogs
import logging
import time
import click
import atexit

import chip.native
import chip.logging

# import chip.FabricAdmin
import chip.CertificateAuthority
from chip.ChipStack import ChipStack

__LOG_LEVELS__ = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "fatal": logging.FATAL,
}


certificateAuthorityManager = None
chipStack = None


def StackShutdown():
    global certificateAuthorityManager
    if not certificateAuthorityManager:
        return
    certificateAuthorityManager.Shutdown()
    chipStack.Shutdown()


@click.group()
@click.pass_context
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(list(__LOG_LEVELS__.keys()), case_sensitive=False),
    help="Determines the verbosity of script output",
)
@click.option(
    "--persistent-storage-json",
    "-p",
    default="/tmp/repl-storage.json",
    show_default=True,
)
@click.option(
    "--paa-trust-store",
    "-t",
    default="./credentials/development/paa-root-certs",
    show_default=True,
)
def main(ctx, log_level, persistent_storage_json, paa_trust_store):
    coloredlogs.install(
        level=__LOG_LEVELS__[log_level], fmt="%(asctime)s %(levelname)-7s %(message)s"
    )
    chip.logging.RedirectToPythonLogging()
    logging.getLogger().setLevel(logging.WARN)
    # logging.getLogger().setLevel(logging.INFO)

    global certificateAuthorityManager
    global chipStack

    chip.native.Init()
    chipStack = ChipStack(
        persistentStoragePath=persistent_storage_json, enableServerInteractions=False
    )
    certificateAuthorityManager = chip.CertificateAuthority.CertificateAuthorityManager(
        chipStack, chipStack.GetStorageManager()
    )

    certificateAuthorityManager.LoadAuthoritiesFromStorage()
    if not certificateAuthorityManager.activeCaList:
        ca = certificateAuthorityManager.NewCertificateAuthority()
        ca.NewFabricAdmin(vendorId=0xFFF1, fabricId=1)
    elif not certificateAuthorityManager.activeCaList[0].adminList:
        certificateAuthorityManager.activeCaList[0].NewFabricAdmin(
            vendorId=0xFFF1, fabricId=1
        )

    caList = certificateAuthorityManager.activeCaList
    devCtrl = caList[0].adminList[0].NewController(paaTrustStorePath=paa_trust_store)
    ctx.obj = {
        "chipStack": chipStack,
        "certificateAuthorityManager": certificateAuthorityManager,
        "devCtrl": devCtrl,
    }

    atexit.register(StackShutdown)
