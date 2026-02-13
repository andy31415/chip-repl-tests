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


async def read_all_impl(devCtrl, node_id, endpoint: None | int):
    path = [(endpoint)] if endpoint is not None else [('*')]
    attr = await devCtrl.ReadAttribute(node_id, path)
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
@click.option("--endpoint", "-e", default=None, type=int, show_default=True)
def read_all(ctx, node_id, endpoint):
    ctx.obj["loop"].run_until_complete(
        read_all_impl(ctx.obj["devCtrl"], node_id, endpoint)
    )


if __name__ == "__main__":
    chipstart.main()
    ChipStack.Shutdown()
