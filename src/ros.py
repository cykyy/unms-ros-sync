try:
    import pyros_api
    from .parser import ParseString
    import os.path
    import json
except Exception as e:
    print(':Error: some Modules in ros.py is missing. {}'.format(e))


class Ros(pyros_api.RosCall):
    prs_obj = ParseString()

    def add_clients_enable_rtr(self, clients):
        crm_clients = clients

        for x in crm_clients:
            _name = x.get('c_ident')
            _password = str(x.get('p_pw'))
            if _password == 'None':
                try:
                    if _password == 'None':
                        _password = self.prs_obj.parse_regdate(x.get('reg_date'))
                except Exception as e:
                    print(':Error: occurred when parsing registration date {}'.format(e))

            _profile = x.get('spack')
            _has_suspended = x.get('has_suspended')
            secret = {
                'c_ident': _name,
                'p_pw': _password,
                'profile': _profile,
                'service_type': 'pppoe',
                'has_suspended': _has_suspended
            }
            self.add_ppp_secret(secret)


def ros_api():

    with open(os.path.abspath(os.path.dirname(__file__))+'/conf.json', 'r') as f:
        dataa = json.load(f)

    m_ip = dataa.get('router_os').get('host')
    username = dataa.get('router_os').get('username')
    password = dataa.get('router_os').get('password')
    port = dataa.get('router_os').get('port')
    plaintext_login = dataa.get('router_os').get('plaintext_login')
    use_ssl = dataa.get('router_os').get('use_ssl')
    ssl_verify = dataa.get('router_os').get('ssl_verify')
    ssl_verify_hostname = dataa.get('router_os').get('ssl_verify_hostname')
    ssl_context = dataa.get('router_os').get('ssl_context')

    x = Ros(username=username, password=password, ros_ip=m_ip, plaintext_login=plaintext_login, port=port,
            use_ssl=use_ssl, ssl_verify=ssl_verify, ssl_verify_hostname=ssl_verify_hostname, ssl_context=ssl_context)

    if x.connection.connected:
        return x
    else:
        x.login()
        return x
