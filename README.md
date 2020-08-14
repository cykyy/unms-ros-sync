#  unms-ros-sync
###  routerOS and UNMS Synchronizer
```sh
Version: 0.0.1
```

unms-ros-sync syncs clients from UNMS to Mikrotik routerOS router. Schedule a crontab to run this script every 5 minutes and you are good to go.\
Everything create/update will get updated once the script runs.

## Usage

### Connection
Edit conf.json with your data. e.g:
```
{
  "ucrm": {
    "ucrm_key": "fdkjfrekDGFnrekvjerCXXgfrSwufrjkferkjfrjkfhbrSDVRGREgvjervFERgvvGVERg",
    "domain_name": "example.com",
    "ip_address": "127.0.0.1"
  },
  "router_os": {
    "host": "192.168.1.1",
    "username": "admin",
    "password": "",
    "port": 8728,
    "plaintext_login": true,
    "use_ssl": false,
    "ssl_verify": true,
    "ssl_verify_hostname": true,
    "ssl_context": null
  }
}
```

#### Parameters:
###### UNMS CRM Module
* `ucrm_key` - String - UCRM API key (create one in System/Security->App Keys). Replace with yours inside quotes
* `domain_name` - String - Domain name of your UNMS
* `ip_address` - String - IP address of your UNMS

###### routerOS
* `host` - String - Hostname or IP of device

Optional Parameters:

* `username` - String - Login username - Default 'admin'
* `password` - String - Login password - Default empty string
* `port` - Integer - TCP Port for API - Default 8728 or 8729 when using SSL
* `plaintext_login` - Boolean - Try plaintext login (for RouterOS 6.43 onwards) - Default **True**
* `use_ssl` - Boolean - Use SSL or not? - Default **False**
* `ssl_verify` - Boolean - Verify the SSL certificate? - Default **True**
* `ssl_verify_hostname` - Boolean - Verify the SSL certificate hostname matches? - Default **True**
* `ssl_context` - Object - Pass in a custom SSL context object. Overrides other options. - Default **None**

Using SSL: If we want to use SSL, we can simply specify `use_ssl` as `True`

### Script Usage Example

```
1. Create a client on CRM module with custom id 'ABC1'
2. Use 'PPP Password' attribute to set password
2. Assign a package e.g '30mbps'
[Make  sure the same '30mbps' package is available in routerOS]
3. Crontab runs the script and 'ABC1' gets created on router.
4. Someone changes password of 'ABC1' on router from winbox.
5. Next 5 minutes the script runs again and updates the password from CRM (meaning to change any value we have to change in CRM. But if we want to achive otherwise then use we have to use 'Custom-Config' tag on CRM clients or archive them on CRM.)
```

## Features & Rules:

- If needed any user to be un-managed from CRM then use the 'Custom-Config' tag on the client or just archive them. Doing so the client will not have any relation with RouterOS! Therefore nothing will get synced with UNMS CRM, the script will gracefully ignore those clients. Thus you can make any changes in the router without worrying about CRM data. Possible use cases e.g: for personal clients or own use PPPoE's.

- If a client is archived on crm but later restored then the admin must reactivate/assign services to the client from the crm client control page. If not then the client will get disabled in RouterOS.

- If admin creates a client without custom/pppoe id on crm then the script will ignore the client and will not get created on routerOS.

- Clients must not be created with custom id that starts with numeric value. e.g.: '1ID'. Instead use 'ID1'. If not followed this rule, unms-ros-sync script will ignore those clients. This is a limitation from routerOS API.

- An invoice that was once properly paid but becomes unpaid later because of editation or payment un-linking will not cause suspension. This only applies if the change happened after the due date of the invoice. If the invoice became unpaid before the due date then it can cause suspension when the due date is reached.

- If a client service has been ended but the admin decides to change password then he/she can so. Change the password on crm client edit page, 'PPP Password' field and the new password will get updated on routerOS PPPoE client though the client is disabled in routerOS and ended on crm.

- If a client is created and in ended state on crm then the client will not get created on routerOS. But if the newly created client is in suspended state then the client will be created and disabled in routerOS as it should.

- If a second package gets added on a client then the second package will get enabled on router regardless of package name or value. The first assigned package will have no effect on routerOS. 

```
Create a custom attribute for clients 'PPP Password'
Place PPPoE password for routerOS there.
If no password is given the the script will get client registration/creation date from crm and use it as password.
The format is, 1482020 (where '14' is day, '8' is month, '2020' is year)
```

- Domain fall back feature has been added. if the specified domain is not available/reachable or the response from api call is greater than 200 then the fall back ip address will be used. This feature is useful in case internet name resolution fails. Then the ip will be used.

```
Supports public ip with public domain.
Supports private ip and public domain with ssl. 
Supports private ip and no domain.
```
## Bonus
'pass_updater.py' is a script included which can be used to import ppp secret password from routerOS to UNMS CRM. If a ppp secret is not available on CRM but exist in routerOS then this script will simply ignore that ppp secret. \
`To use the script, first edit the script and uncomment the bottom portion of the code then save and type 'python3 pass_updater.py' on cli.`

### To-do's

 - Implement static ip and synchronizing with routerOS on crm
 - Got any idea?

### Keyword's

 - 'xg1' means to come back and re-check asap. Possibly no test has been made.
 - 'xg2' means to the solution is temporally and needs more work to solve the problem better.
 - 'xg3?' means is it working as it should? Needs more testing.
 