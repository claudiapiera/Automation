import os
import sys
from netmiko import ConnectHandler
from tools import prettyDict, writeDictIntoFile
from dotenv import load_dotenv

NAME_KEY = 'intf'
IP_KEY = 'ipaddr'
STATUS_KEY = 'status'
DESCR_KEY = 'description'

load_dotenv()
ip = os.getenv('ip')
username = os.getenv('username')
password = os.getenv('password')

device = {
    'device_type': 'cisco_xr',                      #cisco_xe: IOS XE, cisco_xr: IOS XR. try XR
    'ip': ip,
    'username': username,
    'password': password,
    'secret': password,
}

intfs = dict()

#ssh connection
def connect():
    net_connect =ConnectHandler(**device)
    net_connect.enable()
    return net_connect


#save info from 'show ip int brief' command
def sh_int_brief(net_connect):
    global intfs
    output = net_connect.send_command('show ip int brief', use_textfsm=True)
    for intf in output:
        if NAME_KEY in intf:    
            name = intf[NAME_KEY]
            intfs[name] = dict()
        if IP_KEY in intf:
            intfs[name][IP_KEY] = intf[IP_KEY]
        if STATUS_KEY in intf:
            intfs[name][STATUS_KEY] = intf[STATUS_KEY]


def sh_int_description(net_connect):
    global intfs
    output = net_connect.send_command('show interfaces', use_textfsm=True)
    for i in intfs:
        for j in output:
            if i == j['interface']:
                if j[DESCR_KEY] != '':
                    intfs[i][DESCR_KEY] = j[DESCR_KEY]
                break


def create_loopback(net_connect):
    config_commands = [ 'int loopback 13', 'ip address 1.1.1.10 255.255.255.0', 'no sh']
    net_connect.send_config_set(config_commands)
    net_connect.commit()


def prettyWrite(d, f, indent=0):
    for key, value in d.items():
        f.write('\t' * indent + str(key) + " \n")
        if isinstance(value, dict):
            prettyDict(value, indent+1)
        else:
            f.write('\t' * (indent+1) + str(value)+ " \n")


def main():
    net_connect = connect()
    sh_int_brief(net_connect)
    sh_int_description(net_connect)
    create_loopback(net_connect)
    net_connect.disconnect()
    writeDictIntoFile(intfs, "exercise.txt")


if __name__ == '__main__':
    sys.exit(main())
