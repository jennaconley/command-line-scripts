import os
import pynetbox
import requests
from textcolors import (
    black,
    grey,
    red,
    green,
    chartreuse,
    blue,
    magenta,
    cyan,
    rainbow,
    color_menu,
    ColorWheel,
)


def csv_to_dict():
    """
    Extract data from a CSV and return it as a dictionary
    """
    # Get the filepath of the CSV with the host and tag information.
    # csv_filepath = 'hostsandtags.csv'
    try:
        csv_filepath = os.environ["HOSTS_AND_TAGS_CSV"]
    except:
        csv_filepath = input("Please enter CSV file path: ")

    print(cyan(f"\nExtracting data from {csv_filepath} . . ."))
    device_tag_dict = {}
    with open(csv_filepath) as device_file:
        for row_number, row in enumerate(device_file):
            # Remove spaces/tabs/newlines from both ends of the line.
            stripped_row = row.strip()
            # If the row is empty skip it and go on to the next.
            if len(stripped_row) < 1:
                continue
            lowered_row = stripped_row.lower()
            row_list = lowered_row.split(",")
            # Option to skip column headers
            # if row_number == 0:
            #     print(f"Skipping column headers in row {row_number}.")
            #     continue
            device_name = row_list[0]
            device_tag = row_list[1]
            if device_name not in device_tag_dict.keys():
                device_tag_dict[device_name] = [device_tag]
            else:
                device_tag_dict[device_name] = device_tag_dict[device_name].append(
                    device_tag
                )
    print(f"\n{rainbow(device_tag_dict)}")
    return device_tag_dict


def netbox_update_device_tags(device_dict):
    """
    Modify tags of devices in NetBox.
    """
    try:
        netbox_token = os.environ["NETBOX_TOKEN"]
    except:
        netbox_token = input("Please enter Netbox token: ")

    try:
        cert_auth_bundle = os.environ["CERT_AUTH_BUNDLE"]
    except:
        cert_auth_bundle = input("Please enter Certificate Auth Bundle filepath: ")

    color_object = ColorWheel()
    print("\n", color_object.arrows(), "\n")

    requests_session_object = requests.Session()
    requests_session_object.verify = cert_auth_bundle
    netbox_api_object = pynetbox.api(
        url="https://netbox.widgets.com",
        token=netbox_token,
    )
    netbox_api_object.http_session = requests_session_object
    for device_name, tag_list in device_dict.items():
        for device_tag in tag_list:
            try:
                netbox_host = netbox_api_object.dcim.devices.get(name=device_name)

                # # Uncomment to append a tag to a device's list of tags
                # netbox_host.tags.append(device_tag)

                # Add tag/s by concatenating/combining two lists
                # of tags using + (and then replace the old list
                # with the new combined list)
                netbox_host.tags = netbox_host.tags + [device_tag]

                # # Uncomment to remove a tag from a device's list of tags
                # if device_tag in netbox_host.tags:
                #     netbox_host.tags.remove(device_tag)

                # # Formatting to replace a device's entire list of tags with a new list:
                # new_list = ['tag1', 'tag2', 'tag3']
                # netbox_host.tags = new_list

                # Save the changes
                netbox_host.save()

                # Print confirmation (tag lists will be automatically deduplicated later in the process)
                print(
                    color_object.alternate(
                        f"Tags for {device_name}: {netbox_host.tags}"
                    )
                )
            except pynetbox.lib.query.RequestError as error_object:
                print(
                    f"{red('Netbox Error')} for {device_name} --> {error_object.error}"
                )
    print("\n", color_object.arrows(), "\n")


def main():
    device_dict = csv_to_dict()
    netbox_update_device_tags(device_dict)


if __name__ == "__main__":
    main()
