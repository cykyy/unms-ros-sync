try:
    import requests
    import json
    import os.path
except Exception as e:
    print(':Error: some Modules in unmscrm is missing. {}'.format(e))


class CrmCall:
    with open('conf.json', 'r') as f:
        dataa = json.load(f)

    ucrm_key = dataa.get('ucrm').get('ucrm_key')
    domain_name = dataa.get('ucrm').get('domain_name')
    ip_address = dataa.get('ucrm').get('ip_address')

    api_url_base = 'https://' + domain_name + '/crm/api/v1.0/'
    api_url_base_http_ip = 'https://' + ip_address + '/crm/api/v1.0/'
    api_clients = 'clients'
    # api_userident = 'clients?userIdent=MM33'
    api_service_plans = 'service-plans?organizationId=1'
    api_services = 'clients/services?clientId='
    api_attr = 'custom-attributes/2'
    header = {'Content-Type': 'application/json', 'X-Auth-App-Key': ucrm_key}
    api_request_response = ''
    try:
        # Domain fallback feature
        clients_response = requests.get(api_url_base + api_clients, headers=header, timeout=6)  # , verify=False
        api_request_response = clients_response.ok
    except Exception as e:
        print(':Error: occurred during connecting to crm API. {}'.format(e))
    finally:
        if api_request_response is not True:
            clients_response = requests.get(api_url_base_http_ip + api_clients, headers=header, verify=False, timeout=6)

    # getting all the clients with only chosen values. And also ignoring those clients with Custom-Config tag on UNMS.
    def get_crm_clients(self, custom_config=False):
        clients_list_dict = self.clients_response.json()
        final_cleints_ld = clients_list_dict

        # only when True passed and wanted
        if custom_config is True:
            filtered_clients_ld = self.filter_unwanted(clients_list_dict)
            final_cleints_ld = filtered_clients_ld

        crm_clients_all = []
        crm_clients_dict = {}
        for x in final_cleints_ld:
            # the next line of commented codes are only needed if we want to handle numeric clients from here.
            '''
            _numm = '0123456789'
            if x.get('userIdent')[0] in _numm:
                print('h: ', x.get('userIdent') ) '''

            crm_clients_dict.update({'id': x.get('id')})
            crm_clients_dict.update({'c_ident': x.get('userIdent')})

            try:
                y = x.get('attributes')
                # checking if the list is empty or not
                if y:
                    # print('list is not empty')
                    for yy in y:
                        if yy.get('key') == 'pppPassword':
                            crm_clients_dict.update({'p_pw': yy.get('value')})
                            break
                        else:
                            crm_clients_dict.update({'p_pw': None})

                    for yyy in y:
                        if yyy.get('key') == 'staticIp':
                            crm_clients_dict.update({'static_ip': yyy.get('value')})

                # if attribute list is empty then at-least add p_pw to the dictionary
                else:
                    crm_clients_dict.update({'p_pw': None})
            except:
                # can be also set "" xg3?
                crm_clients_dict.update({'p_pw': None})

            crm_clients_dict.update({'has_suspended': x.get('hasSuspendedService')})
            # the next line of code not necessary as when calling all clients crm returns only with non archived
            # clients, so no need isArchive
            crm_clients_dict.update({'reg_date': x.get('registrationDate')})

            crm_clients_all.append(crm_clients_dict.copy())
        return crm_clients_all

    # Getting service package dictionary
    def get_spack(self, _id, first_spack=False):
        api_request_response = ''
        spack_dict = {}  # added later, not verified yet.
        try:
            spack_response = requests.get(self.api_url_base + self.api_services + str(_id),
                                          headers=self.header, timeout=7)  # , verify=False
            spack_dict = spack_response.json()
            api_request_response = spack_response.ok
        except Exception as gs:
            print(':Error: Occurred during getting spack from crm using API. {}'.format(gs))
        finally:
            # Fall back feature. if example.com not working or has any issue with dns or routing the ip, this will
            # be used to make request
            if api_request_response is not True:
                spack_response = requests.get(self.api_url_base_http_ip + self.api_services + str(_id),
                                              headers=self.header, verify=False, timeout=7)
                spack_dict = spack_response.json()
        crm_spack_dict = {}

        if not spack_dict:
            crm_spack_dict.update({'id': _id})
            crm_spack_dict.update({'service_pack': None})
        # also works without else! xg?
        else:
            # only getting the lastly added spack on the client.
            # print('spack dict', spack_dict)
            for x in spack_dict:
                crm_spack_dict.update({'id': x.get('clientId')})
                crm_spack_dict.update({'status': x.get('status')})
                crm_spack_dict.update({'service_pack': x.get('name')})
                # if we want only the first added package only then use first_spack = True
                if first_spack is True:
                    break

        return crm_spack_dict.copy()

    # service package & clients merger function. finds spack for the ids and returns merged list.
    def merge_parse_clients(self, gcc):
        # can also be done by this, in-fact it was at first like this
        crm_clients_all = []
        # discarding all the clients that starts ppp id with numeric value as they complicate staff in routerOS.
        # routerOS-api limitation. if pp-id is full numeric value routerOS-api sends the ppp-id as unique id to
        # mikrotik and mikrotik starts to take the command and disables/enables or execute command on wrong client.
        # eg: on crm there's a client with custom id '4' and there's a client on mikrotik router with name '4' and id
        # '9' also another client ags2 with id '4'. so when this script (routerOS-api) pass command to routerOS with crm
        # id '4' the routerOS assumes the id as unique id and execute commands on ags2 with id '4' wheres we actually
        # meant to execute command on name '4' and id '9'.
        for x in gcc:
            # only accepting clients that start with a alphabetic character.
            _numm = '0123456789'
            # print('hola: ', x.get('c_ident'))
            try:
                if x.get('c_ident') is not None and x.get('c_ident')[0] not in _numm:
                    # print('hola: ', x.get('c_ident'))
                    crm_clients_all.append(x)
            except Exception as mpe:
                print(':Error: probably the pppoe id starts with numeric value {}'.format(mpe))

        # xx here points to crm_clients_all. means whatever changes we make to xx, it gets changed to crm_clients_all
        for xx in crm_clients_all:
            c_id = xx.get('id')

            spack_info_returned = self.get_spack(c_id)
            spack_info_returned_first = self.get_spack(c_id, True)  # getting the first added package. Needs more
            # work. xg3? & xg2 it's a temporary solution. to-do

            if spack_info_returned.get('id') == c_id:
                xx.update({'spack': spack_info_returned.get('service_pack')})
                # getting service status, ie: 1 == active, 2 == suspended
                xx.update({'service_status': spack_info_returned.get('status')})

                # only if spack is not empty and has two spack
                if spack_info_returned.get('service_pack') is not None and spack_info_returned.get('status') != spack_info_returned_first.get('status'):
                    if spack_info_returned_first.get('status') == 1:
                        xx.update({'spack': spack_info_returned_first.get('service_pack')})
                        # getting service status, ie: 1 == active, 2 == suspended
                        xx.update({'service_status': spack_info_returned_first.get('status')})

        return crm_clients_all

    # get only enabled and clients (getting not ended service & not suspended service clients)
    # returning only enabled clients
    def get_enabled_clients_crm(self, csm):
        clients_spack_merged = csm
        ena_clients = []
        for x in clients_spack_merged:
            if x.get('spack') is not None:
                if x.get('service_status') == 1:
                    ena_clients.append(x)
        return ena_clients

    # returns clients who has no package or suspended or ended. hence, returns disabled clients.
    def get_disabled_clients_crm(self, csm):
        clients_spack_merged = csm
        disa_clients = []
        for x in clients_spack_merged:
            if x.get('spack') is not None:
                if x.get('service_status') != 1:
                    disa_clients.append(x)
            # cng:1; needs commenting, because if one is in ended state that client should not get created in routerOS.
            # xg3? cng:2; no! the next line of code needed because if a client gets no-service state from ended then
            # what happens? well, normally should be deleted or at-least disabled in routerOS. to do any of that we need
            # the next line of code
            if x.get('spack') is None:
                disa_clients.append(x)

        return disa_clients

    # unms connection checker
    def check_connection_crm(self):
        _res = False
        try:
            # Domain fallback feature
            clients_response = requests.get(self.api_url_base + self.api_clients,
                                            headers=self.header, timeout=6)  # , verify=False
            _res = clients_response.ok
        except Exception as eccc:
            print(':Error: occurred during connecting to crm API. {}'.format(eccc))
        finally:
            if _res is not True:
                clients_response = requests.get(self.api_url_base_http_ip + self.api_clients,
                                                headers=self.header, verify=False, timeout=6)
                _res = clients_response.ok
        return _res

    # filtering unwanted Custom-Config tagged clients
    def filter_unwanted(self, all_clients):
        filtered = []
        for x in all_clients:
            if x.get('tags'):
                for y in x.get('tags'):
                    # print(type(y))
                    if y.get('name') != 'Custom-Config':
                        filtered.append(x)
            else:
                filtered.append(x)
        return filtered