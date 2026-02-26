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


def pretty_print(attributes_map):
    for endpoint_id, data in attributes_map.items():
        print(f"ENDPOINT {endpoint_id}:")
        for cluster, attrs in sorted(data.items(), key=lambda x: x[0].id):
            print(f"  {cluster.__name__}:")
            for a, value in sorted(
                attrs.items(),
                key=lambda x: x.attribute_id if hasattr(x, "attribute_id") else 0,
            ):
                name = a.__name__
                if hasattr(a, "attribute_id"):
                    name = f"{name} / {a.attribute_id}"

                print(f"    {name:30s}: {value}")


async def read_all_impl(devCtrl, node_id, endpoint: None | int):
    path = [endpoint] if endpoint is not None else ["*"]
    attr = await devCtrl.ReadAttribute(node_id, path)
    pretty_print(attr)
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
