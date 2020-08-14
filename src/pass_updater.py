try:
    import requests
    from src.unmscrm import *
    from .ros import ros_api
    import json
    import os.path
except Exception as eee:
    print(':Error: Some modules are missing. {}'.format(eee))

"""//// This is a one time password importer script from routerOS to unms crm. If you want to use this script then 
first you have to create an custom attribute for client with the 'PPP Password' on ucrm. After creating the attribute 
you will get an 'id' (look at the browser URL bar) on ucrm and you have to put that id below 'values' dictionary 
'customAttributeId' key ***very important***. Only and only after following this guide you can proceed on importing 
pppoe password from routerOS. To proceed you have to uncomment at bottom part of the code and execute this python 
script. 

"""


class UpdateCrmPass:

    with open(os.path.abspath(os.path.dirname(__file__))+'/conf.json', 'r') as f:
        dataa = json.load(f)

    ucrm_key = dataa.get('ucrm').get('ucrm_key')
    domain_name = dataa.get('ucrm').get('domain_name')
    ip_address = dataa.get('ucrm').get('ip_address')

    api_url_base = 'https://' + domain_name + '/crm/api/v1.0/'
    api_url_base_http_ip = 'https://' + ip_address + '/crm/api/v1.0/'

    api_clients = 'clients'
    header = {'Content-Type': 'application/json', 'X-Auth-App-Key': ucrm_key}

    # actual updater function
    def update_ppp_pass(self, client_id, attr_values):
        try:
            # Domain fallback feature
            clients_response = requests.patch(self.api_url_base + self.api_clients+'/'+client_id,
                                              json=attr_values, headers=self.header, timeout=6)  # , verify=False
            api_request_response = clients_response.ok
        except Exception as e:
            print(':Error: occurred during connecting to crm API. {}'.format(e))
        finally:
            if api_request_response is not True:
                clients_response = requests.patch(self.api_url_base_http_ip + self.api_clients+'/'+client_id,
                                                  json=attr_values, headers=self.header, verify=False, timeout=6)

        response_attr = clients_response.json()
        print('response from CRM:', response_attr)

    # parsing data's
    def ppp_pass_updater(self, rtr_c, crm_c):
        values = {
                "attributes": [
                  {
                    "value": "",
                    "customAttributeId": 2
                  }
                ]
              }

        for x in rtr_c:
            for y in crm_c:
                if x.get('c_ident') == y.get('c_ident'):
                    rtr_pass = x.get('p_pw')
                    crm_id = str(y.get('id'))
                    print(crm_id, ' : ', rtr_pass)
                    for xy in values.get('attributes'):
                        xy.update({'value': rtr_pass})

                    print('ppp', y.get('c_ident'), 'updated dict: ', values)
                    self.update_ppp_pass(crm_id, values)


# uncomment below....
'''obj1 = UpdateCrmPass()
obj2 = CrmCall()
ros_api = ros_api()
crm_c = obj2.get_crm_clients()
rtr_c = ros_api.get_ppp_secret()
print('rtr:', rtr_c)
print('crm:', crm_c)

obj1.ppp_pass_updater(rtr_c, crm_c)'''
