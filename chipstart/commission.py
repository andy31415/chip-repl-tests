async def commission_wifi(devCtrl, node_id):
    import aioconsole

    pwd = await aioconsole.ainput("WIFI PWD:")
    await devCtrl.CommissionWiFi(3840, 20202021, node_id, "ManOrAstroMan", pwd)


# OnNetwork is simple, so no separate helper is provided
#    await devCtrl.CommissionOnNetwork(node_id, 20202021)
