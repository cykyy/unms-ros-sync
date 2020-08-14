try:
    import src.unmscrm
    import src.parser
    import src.sync
    import datetime
    from src.ros import ros_api
except Exception as e:
    print(':Error: some modules main.sync are missing {}'.format(e))
print()
print('..........The CRM Script Starting..........')
print(':::::', datetime.datetime.now(), ':::::')

obj1 = src.CrmCall()
ros_api = ros_api()

# checking if the connection with routerOS and UNMS were successfully made
if ros_api.connection.connected is True and obj1.clients_response.ok is True:
    obj3 = src.Sync()

    crmc = obj1.get_crm_clients(custom_config=True)  # passing True if we want to enable the 'Custom-Config' tag.
    crmcm = obj1.merge_parse_clients(crmc)
    ena_crm = obj1.get_enabled_clients_crm(crmcm)
    disa_crm = obj1.get_disabled_clients_crm(crmcm)

    rtrc = ros_api.get_ppp_secret().copy()
    ena_rtr = ros_api.get_enabled_ppp(rtrc).copy()
    disa_rtr = ros_api.get_disabled_ppp(rtrc).copy()

    obj3.sync_enabled(ena_crm, ena_rtr, disa_rtr)

    obj3.sync_disabled(disa_crm, ena_rtr, disa_rtr)

    obj3.sync_password_crm(crmcm, rtrc)

    # disconnecting from routerOS
    ros_api.disconnect()

# for cron logs
print('..........:no-crash: The crm script ended without crashing..........')
print()
