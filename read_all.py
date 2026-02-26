#!/usr/bin/env python

import asyncio
import chipstart
import click
import pprint
import inspect

import matter.clusters as Clusters
from matter.ChipStack import ChipStack


async def commission_impl(devCtrl, node_id):
    await devCtrl.CommissionOnNetwork(node_id, 20202021)
    devCtrl.Shutdown()


def pretty_print(attributes_map):
    for endpoint_id, data in attributes_map.items():
        print(f"ENDPOINT {endpoint_id}:")
        for cluster, attrs in sorted(data.items(), key=lambda x: x[0].id):
            print(f"  {cluster.__name__} / {cluster.id}:")
            for a, value in sorted(
                attrs.items(),
                key=lambda x: x.attribute_id if hasattr(x, "attribute_id") else 0,
            ):
                name = a.__name__
                if hasattr(a, "attribute_id"):
                    name = f"{name} / {a.attribute_id}"

                print(f"    {name:30s}: {value}")


async def read_all_impl(devCtrl, node_id, endpoint: tuple[int], cluster: tuple[str]):
    cluster_names = set()
    cluster_ids = set()
    for c in cluster:
        try:
            cluster_ids.add(int(c))
        except ValueError:
            cluster_names.add(c)

    cluster_types = []
    if len(cluster):
        for name, cl in inspect.getmembers(Clusters, inspect.isclass):
            if not hasattr(cl, "id"):
                continue
            if name in cluster_names:
                cluster_types.append(cl)
                cluster_names.remove(name)
                continue
            if cl.id in cluster_ids:
                cluster_types.append(cl)
                cluster_ids.remove(cl.id)
                continue

    if cluster_names:
        print("Unknown cluster name(s): %r" % cluster_names)

    if cluster_ids:
        print("Unknown cluster id(s): %r" % cluster_ids)

    paths = []
    if not len(endpoint):
        if cluster_types:
            paths = cluster_types  # typle of cluster rs, wildcard endpoint
        else:
            paths = ["*"]
    else:
        paths = [(e, c) for e in endpoint for c in cluster_types]

    attr = await devCtrl.ReadAttribute(node_id, paths)
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
@click.option("--endpoint", "-e", type=int, show_default=True, multiple=True)
@click.option(
    "--cluster",
    "-c",
    default=None,
    type=str,
    show_default=True,
    multiple=True,
    help="Filter for specific clsuter (either by ID or by name)",
)
def read_all(ctx, node_id, endpoint: tuple[int], cluster: tuple[str]):
    ctx.obj["loop"].run_until_complete(
        read_all_impl(ctx.obj["devCtrl"], node_id, endpoint, cluster)
    )


if __name__ == "__main__":
    chipstart.main()
    ChipStack.Shutdown()
