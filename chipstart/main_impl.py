import asyncio
import coloredlogs
import logging
import time
import click
import atexit
import os

import matter.native
import matter.logging

# import matter.FabricAdmin
import matter.CertificateAuthority
from matter.ChipStack import ChipStack
from matter.storage import PersistentStorageJSON

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

def paa_root_path() -> str:
    choices = [
            "./credentials/development/paa-root-certs",
            "../connectedhomeip/credentials/development/paa-root-certs",
            "/home/andrei/connectedhomeip/credentials/development/paa-root-certs"
    ]
    for c in choices:
        if os.path.exists(c):
            return c



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
    default=paa_root_path(),
    show_default=True,
)
def main(ctx, log_level, persistent_storage_json, paa_trust_store):
    coloredlogs.install(
        level=__LOG_LEVELS__[log_level], fmt="%(asctime)s %(levelname)-7s %(message)s"
    )
    matter.logging.RedirectToPythonLogging()
    # logging.getLogger().setLevel(logging.WARN)
    logging.getLogger().setLevel(logging.INFO)

    if not os.path.exists(paa_trust_store):
        raise Exception(f"paa_trust_store not found: {paa_trust_store}")

    global certificateAuthorityManager
    global chipStack

    matter.native.Init()
    chipStack = ChipStack(
        persistentStorage=PersistentStorageJSON(persistent_storage_json),
        enableServerInteractions=False
    )
    certificateAuthorityManager = matter.CertificateAuthority.CertificateAuthorityManager(
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
        "loop": asyncio.new_event_loop(),
    }

    atexit.register(StackShutdown)
