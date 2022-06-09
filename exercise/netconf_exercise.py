import os
import sys
import xmltodict
from ncclient import manager
from argparse import ArgumentParser
from tools import prettyDict, writeDictIntoFile
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('ip')
USERNAME = os.getenv('username')
PASS = os.getenv('password')
PORT = os.getenv('port')

NAME_KEY='interface-name'
IP_KEY='ip-address'
DESCR_KEY='description'
IPV4='ipv4'
ADDRS='addresses'
ADDR='address'


intfs = dict()


def get_schema(device):
    schema = device.get_schema('ietf-interfaces')
    print(schema)


#to get particular version capabilities
def get_version_capabilities(device):
    for cap in device.server_capabilities:
        print(cap)


#filter to obtain only the interfaces info
def get_interfaces(device):
    filter = """
    <filter>
        <interfaces
		xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-interface-cfg">
        </interfaces>
    </filter>"""

    
    xml_config = device.get_config('running', filter).data_xml          #NETCONF getconfig returns the device running configuration filtered in XML
    config = xmltodict.parse(xml_config)                                #transform it into dict

    for intf in config['data']['interfaces']['interface']:
        name = intf[NAME_KEY]
        intfs[name] = dict()
        try:
            intfs[name][IP_KEY] = intf[IPV4][ADDRS][ADDR][ADDR]
        except KeyError:
            pass
        try:
            intfs[name][DESCR_KEY] = intf[DESCR_KEY]
        except KeyError:
            pass
    prettyDict(intfs)


def create_loopback(device):
    configuration = """
    <config>
        <interfaces
		xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-interface-cfg">
            <interface>
                <name>Loopback14</name>
                <config>
                    <name>Loopback14</name>
                    <type
                        xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:softwareLoopback
                    </type>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <ipv4
                            xmlns="http://openconfig.net/yang/interfaces/ip">
                            <addresses>
                                <address>
                                    <ip>2.2.2.3</ip>
                                    <config>
                                        <ip>2.2.2.3</ip>
                                        <prefix-length>32</prefix-length>
                                    </config>
                                </address>
                            </addresses>
                        </ipv4>
                        <ipv6
                            xmlns="http://openconfig.net/yang/interfaces/ip">
                            <addresses>
                                <address>
                                    <ip>fc00::1</ip>
                                    <config>
                                        <ip>fc00::1</ip>
                                        <prefix-length>128</prefix-length>
                                    </config>
                                </address>
                            </addresses>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
            </interface>
        </interfaces>
    </config>"""

    data = device.edit_config(configuration, target='running')        
    print(data)
    #config = xmltodict.parse(xml_config)                                                #transform it into dict


def main():
    device = manager.connect(
                    host=HOST, 
                    username=USERNAME, 
                    password=PASS, 
                    port=PORT)

  #  create_loopback(device)
    get_interfaces(device)
    device.close_session()
    writeDictIntoFile(intfs, "netconf_exercise.txt")


if __name__ == '__main__':
    sys.exit(main())


def connect():
    parser = ArgumentParser(description='Select options.')
    # Input parameters
    parser.add_argument('--host', type=str, required=True,
                        help=HOST)
    parser.add_argument('-u', '--username', type=str, default='cisco',
                        help=USERNAME)
    parser.add_argument('-p', '--password', type=str, default='cisco',
                        help=PASS)
    parser.add_argument('--port', type=int, default=830)
    args = parser.parse_args()
    
    device =  manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password)
    return device