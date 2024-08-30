#!/usr/bin/env python3

import asyncio
import coloredlogs
import logging
import time
import click

import chip.native
import chip.logging
import chip.clusters as Clusters
import chip.FabricAdmin
import chip.CertificateAuthority
from chip.ChipStack import ChipStack

NODE_ID = 1234


def noop(*_):
    pass


async def run_subscribe_loop(devCtrl):
    global NODE_ID

    for i in range(10):
        print(f"TEST {i + 1}...")
        test_start = time.time()
        subscription = await devCtrl.ReadAttribute(
            NODE_ID, [()], returnClusterObject=True, reportInterval=(0, 30)
        )

        print("Priming done:")
        print("  onoff:", subscription.GetAttributes()[1][Clusters.OnOff].onOff)

        # make the attribute updates less spammy
        subscription.SetAttributeUpdateCallback(noop)

        try:
            await asyncio.sleep(3600)
        finally:
            subscription.Shutdown()
        print("TEST DURATION: %s" % (time.time() - test_start))


async def run_toggle_loop(devCtrl):
    global NODE_ID

    for i in range(10):
        print(f"TEST {i + 1}...")
        test_start = time.time()
        subscription = await devCtrl.ReadAttribute(
            NODE_ID, [()], returnClusterObject=True, reportInterval=(0, 30)
        )

        print("Priming done:")
        print("  onoff:", subscription.GetAttributes()[1][Clusters.OnOff].onOff)

        # make the attribute updates less spammy
        subscription.SetAttributeUpdateCallback(noop)

        try:
            currentState = subscription.GetAttributes()[1][Clusters.OnOff].onOff
            for i in range(100):
                command_time = time.time()
                await devCtrl.SendCommand(1234, 1, Clusters.OnOff.Commands.Toggle())
                while True:
                    try:
                        if (
                            subscription.GetAttributes()[1][Clusters.OnOff].onOff
                            != currentState
                        ):
                            break
                    except:
                        pass  # busy
                    await asyncio.sleep(0.1)
                print(
                    "%3d: Toggle detected after %s"
                    % (i + 1, time.time() - command_time)
                )

                currentState = subscription.GetAttributes()[1][Clusters.OnOff].onOff
        finally:
            subscription.Shutdown()
        print("TEST DURATION: %s" % (time.time() - test_start))


async def read_heap(devCtrl):
    global NODE_ID
    attr = await devCtrl.ReadAttribute(
        NODE_ID, [Clusters.SoftwareDiagnostics.Attributes.CurrentHeapFree]
    )
    print(attr)


async def commission(devCtrl):
    global NODE_ID
    import aioconsole

    pwd = await aioconsole.ainput("WIFI PWD:")
    await devCtrl.CommissionWiFi(3840, 20202021, NODE_ID, "ManOrAstroMan", pwd)


@click.group()
@click.pass_context
def main(ctx):
    coloredlogs.install(level="DEBUG")
    chip.logging.RedirectToPythonLogging()
    logging.getLogger().setLevel(logging.WARN)
    # logging.getLogger().setLevel(logging.INFO)

    chip.native.Init()
    chipStack = ChipStack(
        persistentStoragePath="/tmp/repl-storage.json", enableServerInteractions=False
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
    devCtrl = (
        caList[0]
        .adminList[0]
        .NewController(paaTrustStorePath="./credentials/development/paa-root-certs")
    )
    ctx.obj = {
        "chipStack": chipStack,
        "certificateAuthorityManager": certificateAuthorityManager,
        "devCtrl": devCtrl,
    }


@main.command()
@click.pass_context
def commission(ctx):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(commission(ctx.obj["devCtrl"]))


@main.command()
@click.pass_context
def loop_subscribe(ctx):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_subscribe_loop(ctx.obj["devCtrl"]))


@main.command()
@click.pass_context
def loop_toggle(ctx):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_toggle_loop(ctx.obj["devCtrl"]))


@main.command()
@click.pass_context
def heap(ctx):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_heap(ctx.obj["devCtrl"]))


if __name__ == "__main__":
    main()
