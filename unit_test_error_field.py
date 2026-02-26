#!/usr/bin/env python

import asyncio
import chipstart
import click
import pprint

import matter.clusters as Clusters
from matter.ChipStack import ChipStack


async def commission_impl(devCtrl, node_id):
    await devCtrl.CommissionOnNetwork(node_id, 20202021)
    devCtrl.Shutdown()


async def read_failure_impl(devCtrl, node_id):
    attr = await devCtrl.ReadAttribute(
        node_id, [(1, Clusters.UnitTesting.Attributes.FailureInt32U)]
    )
    pprint.pprint(attr)
    devCtrl.Shutdown()


@chipstart.main.command()
@click.pass_context
@click.option("--node-id", "-n", default=1234, show_default=True)
def commission(ctx, node_id):
    ctx.obj["loop"].run_until_complete(commission_impl(ctx.obj["devCtrl"], node_id))


@chipstart.main.command()
@click.pass_context
@click.option("--node-id", "-n", default=1234, show_default=True)
def read_failure(ctx, node_id):
    ctx.obj["loop"].run_until_complete(read_failure_impl(ctx.obj["devCtrl"], node_id))


if __name__ == "__main__":
    chipstart.main()
    ChipStack.Shutdown()
