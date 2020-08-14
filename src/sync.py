try:
    from src.unmscrm import *
    from src.parser import *
    from .ros import ros_api
except Exception as e:
    print(':Error: some modules are missing. {}'.format(e))


class Sync:
    try:
        ros_api = ros_api()
        prs_obj = ParseString()
    except Exception as es:
        print('Error occurred during creating objects in sync. {}'.format(es))

    def sync_password_crm(self, all_crm_clients, all_rtr_clients):
        for x in all_crm_clients:
            for y in all_rtr_clients:
                if x.get('c_ident') == y.get('c_ident'):
                    try:
                        if x.get('p_pw') != y.get('p_pw'):
                            _password = x.get('p_pw')
                            if _password is None:
                                _password = self.prs_obj.parse_regdate(x.get('reg_date'))
                                if _password != y.get('p_pw'):
                                    self.ros_api.update_secret_password(y.get('c_ident'), _password)
                            else:
                                self.ros_api.update_secret_password(y.get('c_ident'), _password)
                    except Exception as espc:
                        print(espc)

    def sync_enabled(self, ena_c_crm, ena_c_rtr, disa_c_rtr):
        ena_clients_crm = ena_c_crm
        ena_clients_rtr = ena_c_rtr
        disa_clients_rtr = disa_c_rtr
        ena_matched_clients_crm = []  # those who matched in both place, authority crm
        ena_unmatched_clients_crm = []  # those who didn't matched in both place, authority crm

        for x_ena_c in ena_clients_crm:
            for y_ena_r in ena_clients_rtr:
                if x_ena_c.get('c_ident') == y_ena_r.get('c_ident'):
                    ena_matched_clients_crm.append(x_ena_c)

                    # checking if a enabled client package has been changed or not, if changed call package update
                    # function
                    if x_ena_c.get('spack') is not None:
                        if x_ena_c.get('spack') != y_ena_r.get('profile'):
                            self.ros_api.update_secret_profile(y_ena_r.get('c_ident'), x_ena_c.get('spack'))

        # printing both place enabled and available
        # print('first matched:', ena_matched_clients_crm)
        for x in ena_clients_crm:
            if x not in ena_matched_clients_crm:
                ena_unmatched_clients_crm.append(
                    x)  # getting non-matched clients. those who are not in same state in routerOS

        # printing clients that are not enabled or not available in mikrotik
        # print(ena_unmatched_clients_crm)
        new_clients = ena_unmatched_clients_crm.copy()
        temp_new_clients = new_clients.copy()

        print('Enabled Now in RTR(ena):', end=' ')
        # checking if we are still connected with routerOS or not xg1
        if self.ros_api.check_connection_ros() is True:
            # comparing crm previously unmatched rtr enabled clients with rtr disabled clients
            for unmatched in temp_new_clients:  # cng:1; ena_unmatched_clients_crm; where cng:1 means recently it was
                # active and needs more taste
                for disa_rt in disa_clients_rtr:
                    if unmatched.get('c_ident') == disa_rt.get('c_ident'):
                        # clients enabled in crm but disabled in rtr -> needs actions

                        # now calling function and passing client id to enable disabled client
                        try:
                            # checking if a enabled client package has been changed or not, if changed call package
                            # update function
                            if unmatched.get('spack') is not None:
                                if unmatched.get('spack') != disa_rt.get('profile'):
                                    self.ros_api.update_secret_profile(disa_rt.get('c_ident'), unmatched.get('spack'))

                            # passing to enable this client
                            _try_res = self.ros_api.set_ppp_enable(
                                unmatched.get('c_ident'))  # passing client to enable in router from disable state
                        except Exception as seu:
                            print(seu)
                        finally:
                            if _try_res is False:
                                print(':Error: executing command on RTR')
                        print(unmatched.get('c_ident'), end=', ')  # printing for log, which client is disabling
                        new_clients.remove(unmatched)
        print()
        # checking of routerOS connection for this time is handled from the rtr adder function itself
        # now creating clients who do not exist in router.
        try:
            self.ros_api.add_clients_enable_rtr(new_clients)
        except Exception as esa:
            print(':Error: during adding clients! {}'.format(esa))

        # printing logs.
        # print('to create: ', new_clients)
        print('Created Now in RTR(ena):', end=' ')
        for _to_log in new_clients:
            if _to_log.get('spack') in self.ros_api.get_profile():
                print(_to_log.get('c_ident'), end=', ')
        print()

    def sync_disabled(self, disa_c_crm, ena_c_rtr, disa_c_rtr):
        disa_clients_crm = disa_c_crm
        ena_clients_rtr = ena_c_rtr
        disa_clients_rtr = disa_c_rtr
        disa_matched_clients_crm = []
        disa_unmatched_clients_crm = []
        to_create = []
        for x_disa_c in disa_clients_crm:
            for y_disa_r in disa_clients_rtr:
                if x_disa_c.get('c_ident') == y_disa_r.get('c_ident'):
                    # finding disabled clients in rtr
                    disa_matched_clients_crm.append(x_disa_c)

                    # checking if a enabled client package has been changed or not, if changed call package update
                    # function
                    if x_disa_c.get('spack') is not None:
                        if x_disa_c.get('spack') != y_disa_r.get('profile'):
                            self.ros_api.update_secret_profile(y_disa_r.get('c_ident'), x_disa_c.get('spack'))

        # printing both place disabled and available clients
        # print('initial matched:', disa_matched_clients_crm)
        # getting unmatched clients, those who are not in the same state as in crm
        for x in disa_clients_crm:
            if x not in disa_matched_clients_crm:
                disa_unmatched_clients_crm.append(x)

        # printing clients that are not enabled or not available in mikrotik
        # prints only those clients who is not created in rtr but created and disabled in ucrm
        # print('not enabled or not available: ', disa_unmatched_clients_crm)
        print('Not exist in RTR(disa) & not enabled in CRM:', end=' ')
        for _to_log in disa_unmatched_clients_crm:
            print(_to_log.get('c_ident'), end=', ')
        print()

        new_clients = disa_unmatched_clients_crm.copy()
        # checking if they are enabled or not
        temp_new_clients = new_clients.copy()
        print('Disabled Now in RTR(disa):', end='')
        # checking if we are still connected with routerOS or not xg1
        if self.ros_api.check_connection_ros() is True:
            for unmatched in temp_new_clients:
                for ena_rt in ena_clients_rtr:  # now comparing with routerOS enabled list
                    if unmatched.get('c_ident') == ena_rt.get('c_ident'):
                        # clients disabled in crm but enabled in rtr -> needs actions

                        # now calling function and passing client id to disable enable client
                        # print('count')
                        _try_res = ''
                        try:
                            _try_res = self.ros_api.set_ppp_disable(
                                unmatched.get('c_ident'))  # also can return response and condition it and do the rest
                            if _try_res:
                                self.ros_api.remove_active_ppp_secret(unmatched.get('c_ident'))
                        except Exception as sd:
                            print(':Error: on sync disabled', sd)
                        finally:
                            if _try_res is False:
                                print(':Error: executing command on RTR')

                        print(unmatched.get('c_ident'), end=', ')  # for logs
                        disa_matched_clients_crm.append(unmatched)
                        new_clients.remove(unmatched)  # not needed for now
        print()  # line break

        # checking if the user has any package or not on crm. if not then it is also discarded from to_create
        for x in disa_clients_crm:  # also can be used disa_unmatched_clients_crm here
            if x not in disa_matched_clients_crm:
                # only telling to create who has a service and or either in active state or suspend state in crm
                if x.get('spack') is not None and (x.get('service_status') == 1 or x.get('service_status') == 3):
                    to_create.append(x)
        # print(to_create)

        # passing clients to create them because these clients are not available in mikrotik but available in crm
        try:
            _try_res_two = self.ros_api.add_clients_enable_rtr(to_create)
        except Exception as addce:
            print(':Error: during creating brand new clients! {}'.format(addce))
        finally:
            if _try_res_two is False:
                print(':Error: executing command on RTR')

        print('Created Now ena/disa clients of crm who are not available in RTR(disa): ', end='')
        for _to_log in to_create:
            print(_to_log.get('c_ident'), end=', ')
        print()
