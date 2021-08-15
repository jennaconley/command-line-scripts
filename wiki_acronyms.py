"""
This script uses an environment variable: CERT_AUTH_BUNDLE
The machine running it must also have Python 3 and the Python requests module installed.
It gets acronym definitions published on a private wiki, parses them, and saves them in csv format.

"""
import json
import os
import re
import requests
import sys
import time

def get_acronyms():
    cert_auth_bundle = os.environ['CERT_AUTH_BUNDLE']

    # ord() returns an integer representing a Unicode character
    # chr() turns the integer back into a character
    letter_list = [chr(each) for each in range(ord('A'), ord('Z') + 1)]
    acronym_dict = {}

    for letter in letter_list:
        url = f'https://wiki.widgetsinc.com/widgetwiki/api.php?action=parse&page=Acronyms/{letter}&prop=wikitext&format=json'
        response_object = requests.get(url, verify=cert_auth_bundle)
        response_object.encoding = "UTF-8"
        if response_object.status_code == 200:
            result_dict = json.loads(response_object.text)
            wikitext = result_dict['parse']['wikitext']['*']
            wikitext = wikitext.replace("{{TOCabc}}", "")
            wikitext = wikitext.replace("<br>", "")
            text_list = wikitext.split("\n*")
            for index, acronym_info in enumerate(text_list):
                if ("http://" in acronym_info) or ("https://" in acronym_info):
                    split_on_comma_list = acronym_info.split(',')
                    no_links_list = []
                    for phrase in split_on_comma_list:
                        if ("http://" in phrase) or ("https://" in phrase):
                            split_on_space_list = phrase.split(" ")
                            new_tiny_list = []
                            for word in split_on_space_list:
                                if ("http://" in word) or ("https://" in word):
                                    continue
                                else:
                                    new_tiny_list.append(word)
                            phrase = ' '.join(new_tiny_list)
                            no_links_list.append(phrase)
                        else:
                            no_links_list.append(phrase)
                    acronym_info = ','.join(no_links_list)
                acronym_list = re.split(',.', acronym_info)
                if len(acronym_list) > 1:
                    for item_index, item in enumerate(acronym_list):
                        item = item.replace("[", "")
                        item = item.replace("]", "")
                        item = item.strip(" \r'\n")
                        if "|" in item:
                            item = item.split("|")[1]
                        if "\n" in item:
                            item = item.split("\n")[0]
                        if "\'\'\'" in item:
                            split_on_quotes_list = item.split("\'\'\'")
                            for subindex, substring in enumerate(split_on_quotes_list):
                                substring = substring.strip(" \n\r")
                                if subindex == 0:
                                    acronym_key = substring
                                    if acronym_key not in acronym_dict.keys():
                                        acronym_dict[acronym_key] = []
                                else:
                                    acronym_dict[acronym_key] = acronym_dict[acronym_key] + [substring]
                            continue
                        item = item.strip(" \n\r")
                        if item_index == 0:
                            acronym_key = item
                            if acronym_key not in acronym_dict.keys():
                                acronym_dict[acronym_key] = []
                        else:
                            acronym_dict[acronym_key] = acronym_dict[acronym_key] + [item]
        else:
            print(response_object.status_code, response_object.text)
    return(acronym_dict)


def get_wiki_link(potential_page_name):
    cert_auth_bundle = os.environ['CERT_AUTH_BUNDLE']

    page_name_with_underscores = potential_page_name.replace(" ", "_")
    try:
        url = f'https://wiki.widgetsinc.com/widgetwiki/index.php/{page_name_with_underscores}'
        response_object = requests.get(url, verify=cert_auth_bundle)
        response_object.raise_for_status()
        page_link = url
    except requests.exceptions.RequestException as error_object:
        print(f"Request for {url} failed: {type(error_object)} --> {error_object}")
        page_link = None
    return(page_link)


if __name__ == "__main__":
    beginning = time.time()
    acronym_dict = get_acronyms()
    output_file = "acronyms.csv"
    with open(output_file, "w") as file_object:
        for key, value_list in acronym_dict.items():
            for value in value_list:
                page_link = get_wiki_link(value)
                if page_link:
                    line = f"{key},{value},{page_link},"
                else:
                    line = f"{key},{value},,"
                file_object.write(f"{line}\n")
                # sys.exit(0)

    print(f"\nFinished! It took {(time.time() - beginning):.0f} seconds.\n")
