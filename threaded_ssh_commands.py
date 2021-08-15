import os
import paramiko
import pynetbox
import requests
import threading
import urllib3

active_host_lock = threading.Lock()
command_output_lock = threading.Lock()
active_hosts_list = []
standby_hosts_list = []
weird_hosts_list = []
command_output_dict = {}


def get_netbox_hosts():
    requests_session_object = requests.Session()
    requests_session_object.verify = os.environ['CERT_AUTH_BUNDLE']
    netbox_api_object = pynetbox.api(url='https://netbox.widgets.com', token=os.environ['NETBOX_API_TOKEN'])
    # Telling pynetbox to use the requests session just configured as its session
    netbox_api_object.http_session = requests_session_object
    netbox_hosts = netbox_api_object.dcim.devices.filter(tag="devices_of_interest", site="widgets_inc_data_center")
    netbox_host_stings_list = []
    for host in netbox_hosts:
        netbox_host_stings_list.append(host.name)
    return(netbox_host_stings_list)


def execute_command_on_host(host):
    # Telling Python to use the global version 
    # of this variable instead of the function-specific
    # local version it would usually use.
    global command_output_dict

    username = os.environ['DEVICE_USERNAME']
    password = os.environ['DEVICE_PASSWORD']
    port = 22
    command_string = os.environ['DEVICE_UPTIME_COMMAND']

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(f"{host}.widgets.com", port, username, password)
    stdin, stdout, stderr = ssh.exec_command(command_string)
    outlines = stdout.readlines()
    command_output = ''.join(outlines)
    ssh.close()

    # Without this lock we might have two threads trying to change the same
    # data structure at the same time.
    with command_output_lock:
        command_output_dict[host] = command_output


def execute_command_on_active_list(active_hosts_list):
    # Telling Python to use the global version 
    # of this variable instead of the function-specific
    # local version it would usually use.
    global command_output_dict
    
    # Attempting threading
    thread_objects_list = []
    # Create each thread, assign each a target function and a host, 
    # and collect them in a list.
    for host in active_hosts_list:
        thread_objects_list.append(threading.Thread(target=execute_command_on_host, name=f"<{host} thread>", args=(host,)))

    # Tell each thread to start running its target function.
    for thread_object in thread_objects_list:
        thread_object.start()

    # Tell the main thread to wait for each of the other 
    # threads to finish and rejoin it before continuing.
    for thread_object in thread_objects_list:
        thread_object.join(timeout=15.0)
    
    active_threads_list = threading.enumerate()
    for active_thread_object in active_threads_list:
        print("\nActive after all threads have joined:", active_thread_object.name, "\n")
    
    return(command_output_dict)


def check_host_active_status(host):
    # Telling Python to use the global versions 
    # of these variables instead of the function-specific
    # local versions it uses by default.
    global active_hosts_list
    global standby_hosts_list
    global weird_hosts_list

    username = os.environ['DEVICE_USERNAME']
    password = os.environ['DEVICE_PASSWORD']
    port = 22
    command_string = os.environ['DEVICE_STATUS_COMMAND']

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(f"{host}.widgets.com", port, username, password)
    stdin, stdout, stderr = ssh.exec_command(command_string)
    outlines = stdout.readlines()
    status = ''.join(outlines)
    ssh.close()

    # Without this lock we might have two threads trying to change the same
    # data structure at the same time.
    with active_host_lock:
        if "active" in status:
            active_hosts_list.append(host)
        elif "standby" in status:
            standby_hosts_list.append(host)
        else:
            print(f"{host}^device was not active or standby - {status}")
            weird_hosts_list.append(host)


def create_list_of_active_hosts(netbox_host_stings_list):
    # Telling Python to use the global versions 
    # of these variables instead of the function-specific
    # local versions it uses by default.
    global active_hosts_list
    global standby_hosts_list
    global weird_hosts_list

    # Attempting threading
    thread_objects_list = []
    # Create each thread, assign each a target function and a host,
    # and collect them in a list.
    for host in netbox_host_stings_list:
        thread_objects_list.append(threading.Thread(target=check_host_active_status, args=(host,)))

    # Tell each thread to start running its target function.
    for thread_object in thread_objects_list:
        thread_object.start()

    # Tell the main thread to wait for each of the other 
    # threads to finish and rejoin it before continuing.
    for thread_object in thread_objects_list:
        thread_object.join(timeout=15.0)
    print("Standby host list:", standby_hosts_list)
    print("Standby host count:", len(standby_hosts_list))
    print("Active host list:", active_hosts_list)
    print("Active host count:", len(active_hosts_list))
    print("Other host list:", weird_hosts_list)
    return(active_hosts_list)


def main():
    netbox_host_stings_list = get_netbox_hosts()
    print(f"\nFound {len(netbox_host_stings_list)} hosts in Netbox: {netbox_host_stings_list}")

    active_host_list = create_list_of_active_hosts(netbox_host_stings_list)
    
    command_output_dict = execute_command_on_active_list(active_host_list)

    for host, output in command_output_dict.items():
        print(f"{host} => {output}")


if __name__ == "__main__":
    main()
