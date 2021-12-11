import logging


def get_ip_list_from_csv(csv_filename):
    ip_list = []
    with open(csv_filename) as file_object:
        for row_number, row in enumerate(file_object):
            # Remove spaces/tabs/newlines from both ends of the line.
            ip_trimmed = row.strip()
            # If the row is empty skip it and go on to the next.
            if len(ip_trimmed) < 1:
                logging.info(
                    f"No data found on line {row_number} (Note: line numbers are 0-indexed)"
                )
                continue
            logging.debug(f"Reading line {row_number}: {ip_trimmed}")
            ip_list.append(ip_trimmed)
    return ip_list


def count_ips_from_csv(ip_list):
    """
    Count how many times an IP shows up in the list using a dictionary
    """
    # Create an empty dictionary
    ip_count_dict = {}

    # Add 1 for each time an IP shows up in the list
    for ip_string in ip_list:
        ip_count_dict[ip_string] = ip_count_dict.get(ip_string, 0) + 1
    return ip_count_dict


def select_count_value(ip_count_tuple):
    return ip_count_tuple[1]


def sort_dictionary_by_value(unsorted_dict):
    key_value_tuples_iterator = unsorted_dict.items()

    #### Option 1: sorting with keys created by a lambda function
    # sorted_tuples_list = sorted(key_value_tuples_iterator, key=lambda ip_count_tuple: ip_count_tuple[1])
    #
    #### Option 2: sorting with keys created by a function defined seperately (above)
    sorted_tuples_list = sorted(key_value_tuples_iterator, key=select_count_value)

    sorted_ip_dict = {}
    for ip, count in sorted_tuples_list:
        sorted_ip_dict[ip] = count
    return sorted_ip_dict


def main():
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)

    ip_list = get_ip_list_from_csv("arps.csv")
    logging.debug(f"IP list: {ip_list}")
    ip_list_length = len(ip_list)
    logging.info(f"Found {ip_list_length} IPs in csv")

    ip_count_dict = count_ips_from_csv(ip_list)

    sorted_ip_dict = sort_dictionary_by_value(ip_count_dict)

    with open("ip_counts_sorted.csv", "w") as file_object:
        for ip, count in sorted_ip_dict.items():
            logging.info(f"{ip}: {count}")
            file_object.write(f"{ip},{count}\n")


if __name__ == "__main__":
    main()
