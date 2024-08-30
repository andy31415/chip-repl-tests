#!/usr/bin/env python

import asyncio
import chipstart
import click
import pprint

import chip.clusters as Clusters
from chip.ChipStack import ChipStack


async def commission_impl(devCtrl, node_id):
    await devCtrl.CommissionOnNetwork(node_id, 20202021)
    devCtrl.Shutdown()


async def read_heater_types_impl(devCtrl, node_id):
    attr = await devCtrl.ReadAttribute(
        node_id, [Clusters.WaterHeaterManagement.Attributes.HeaterTypes]
    )
    pprint.pprint(attr)
    devCtrl.Shutdown()


@chipstart.main.command()
@click.pass_context
@click.option("--node-id", "-n", default=1234, show_default=True)
def commission(ctx, node_id):
    asyncio.get_event_loop().run_until_complete(
        commission_impl(ctx.obj["devCtrl"], node_id)
    )


@chipstart.main.command()
@click.pass_context
@click.option("--node-id", "-n", default=1234, show_default=True)
def read_heater_types(ctx, node_id):
    asyncio.get_event_loop().run_until_complete(
        read_heater_types_impl(ctx.obj["devCtrl"], node_id)
    )


if __name__ == "__main__":
    chipstart.main()
    ChipStack.Shutdown()
