import os
import sys
import paramiko
import textfsm
import tempfile
import pprint
import pandas as pd

from tools import writePickleFile, readPickleFile
from numpy import empty
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')

DESCR_KEY = 'DESCR'
NAME = 0
UPDOWN = 1
FILENAME = 'mapping.xlsx'
SHEETNAME = 'IOS-XR'
INTFS_FILENAME = 'challenge.pickle'

#TextFSM template for 'show ip interface brief' command
template_show_ip_int_brief = r"""Value INTF (\S+)
Value ADDR (\S+)
Value STATUS (Up|Down|administratively down|Shutdown)
Value PROTO (Up|Down)

Start
  ^${INTF}\s+${ADDR}\s+${STATUS}\s+${PROTO}\s+\w -> Record
  """

template_show_descr = r"""Value INTF (\S+)
Value STATUS (up|down|admin-down|shutdown)
Value PROTO (up|down)
Value DESCR (.*)

Start
  ^${INTF}\s+${STATUS}\s+${PROTO}\s+${DESCR} -> Record
""" 

intfs = dict()

#Establishes SSH connection with Paramiko
def sshConnection():
    ssh = paramiko.SSHClient()                                                  # Create SSH object
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())                   # Allow connections to hosts that aren't in the 'know_hosts' file
    ssh.connect(hostname=HOST, port=PORT, username=USERNAME, password=PASSWORD, banner_timeout=200)      # Server connection
    return ssh


#Parses command output to TextFSM template
def parse_textfsm(template, output):
    tmp = tempfile.NamedTemporaryFile(delete=False)                             # Create temp file to hold template

    # Write template to file for textfsm
    with open(tmp.name, 'w') as f:
        f.write(template)

    # Get read handle for textfsm
    with open(tmp.name, 'r') as f:
        fsm = textfsm.TextFSM(f)                                                # Instantiate a new TextFSM wrapper
        fsm_results = fsm.ParseText(output)                                     # Parse the output text according to template rules.
        parsed = [dict(zip(fsm.header, row)) for row in fsm_results]            # Convert to list of dictionaries since TextFSM may return multiple 'row' results.

    return parsed


#Creates ssh connection and tries sending command sent by parameter
def send_command(command):
    try:
        ssh = sshConnection()

        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.close()                                           # Close this handle, not using it.
        # Read regular stdout and std err
        output_ok = stdout.read()
        output_err = stderr.read()
        # Return error text if exist else regular std out.
        # Convert to utf-8 string since python3 paramiko gives byte object
        ssh.close()
        if output_err:
            value = output_err.decode('utf-8')
        else:
            value = output_ok.decode('utf-8')  
        return value  
    except:
        return 'EOF'


#Gets interfaces description and saves it into dictionary
#Slow function because creates ssh connection each time
def getIntfsDescr(intfs):               
    for i in intfs:
        command = 'show interface ' + i['INTF'] + ' description'
        output_descr = send_command(command)                                        
        intf = parse_textfsm(template=template_show_descr, output=output_descr)
        if intf:                                                                   #if there is an output from command sent
            i['Description'] = intf[0][DESCR_KEY]                                  #save description


#gets description and saves it into interfaces dictionary using a mapping file
def getDescription(output):
    def getInterfaceInfo():
        info = line.split(' ') 
        info = list(filter(None, info))
        print(info)
        info.pop(UPDOWN)
        info.pop(UPDOWN)
        return info

    def getPathFile():
        path = os.path.dirname(os.path.abspath(__file__))
        return path + '/' + FILENAME
    
    def readMapping():
        df = pd.read_excel(io=getPathFile(), sheet_name=SHEETNAME)
        return df.to_dict() 
    
    def saveDescription():
        listLength = len(info)
        for i in intfs:
            if i['INTF'] == intf_name:
                if listLength > 1:
                    i['Description'] = ' '.join(info)
                if listLength == 1:
                    i['Description'] = info[0]
                break
    
    mapping = readMapping()
    startIntfList = False
    for line in output.split('\r\n'):
        if line != ('') and startIntfList is True:
            info = getInterfaceInfo()
            for value in mapping['Abbreviation']:
                if info[NAME] == mapping['Abbreviation'][value]:
                    intf_name = mapping['Name'][value]
                    info.pop(NAME)
                    if info is not empty:
                        saveDescription()
                    break
        if line != ('')  and line[0] == '-':
            startIntfList = True


def main():
    global intfs
    print("hello world")
    output_brief = send_command('show ip interface brief')
    intfs = parse_textfsm(template=template_show_ip_int_brief, output=output_brief)
    output_descr = send_command('show interfaces description')
    getDescription(output_descr)
    writePickleFile(intfs, INTFS_FILENAME)
    data = readPickleFile(INTFS_FILENAME)
    pprint.pprint(data)


if __name__ == '__main__':
    sys.exit(main())
    #internal github
    #read from CDB, same exercise: ip @, name, etc.
    #create package: sync, package reload, device name input for YANG, then extract intfs info