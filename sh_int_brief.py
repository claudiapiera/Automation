import cli
import sys

NAME = 0
ADDRESS = 1
STATUS = 4

intfs = dict()

# Grabs list of interfaces from passed in data. 
def grab_intf(i):
    global intfs
    # If the passed in data is empty exit the function. 
    if i == "":
        return 
    #regular expressions
    intf_info = (i.split(' '))    
    name = intf_info[NAME]
    ip = intf_info[ADDRESS]
    status = intf_info[STATUS]

    # Assign the interface name as another dictionary. nested dict.
    intfs[name] = dict()
    intfs[name]['ip:address'] = ip
    intfs[name]['int-status'] = status


def main():
    output = print cli.execute('show ip int brief')
    # Take the command output
    for i in output.split('\n'):
        grab_intf(i)


if __name__ == '__main__':
    sys.exit(main())

