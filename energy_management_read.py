#!/usr/bin/env python

import click
import chipstart
import asyncio
import chip.clusters as Clusters


async def commission_impl(devCtrl, node_id):
    await devCtrl.CommissionOnNetwork(node_id, 20202021)


async def read_heater_types_impl(devCtrl, node_id):
    attr = await devCtrl.ReadAttribute(
        node_id, [Clusters.WaterHeaderManagement.Attributes.HeaterTypes]
    )
    print(attr)


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
