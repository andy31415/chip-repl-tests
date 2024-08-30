import asyncio
import coloredlogs
import logging
import time
import click

import chip.native
import chip.logging

# import chip.FabricAdmin
import chip.CertificateAuthority
from chip.ChipStack import ChipStack


@click.group()
@click.pass_context
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
def main(ctx, persistent_storage_json, paa_trust_store):
    coloredlogs.install(level="DEBUG")
    chip.logging.RedirectToPythonLogging()
    logging.getLogger().setLevel(logging.WARN)
    # logging.getLogger().setLevel(logging.INFO)

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
