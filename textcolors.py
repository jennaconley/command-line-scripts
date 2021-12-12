"""
Text formatting with colors!
(Developed for Python scripts run from a bash terminal on MacOS - not tested in other environments.)
"""

color_dictionary = {
    "black": "30",
    "red": "31",
    "green": "32",
    "chartreuse": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "grey": "37",
}

for color, color_code in color_dictionary.items():
    exec(f'''
def {color}(text_string):
    return(f"\033[0;{color_code}m{{text_string}}\033[0m")
    ''')

def rainbow(input_to_be_formatted, color_dict=color_dictionary):
    color_list = list(color_dict.keys())
    text_string = str(input_to_be_formatted)
    text_list = text_string.split(" ")
    color_formatted_list = []
    for text_index, text_item in enumerate(text_list):
        remainder_int = text_index % len(color_list)
        current_color = color_list[remainder_int]
        color_formatted_text = (
            f"\033[0;{color_dictionary[current_color]}m{text_item}\033[0m"
        )
        color_formatted_list.append(color_formatted_text)
    final_formatted_string = " ".join(color_formatted_list)
    return final_formatted_string


def color_menu(color_dict=color_dictionary):
    color_coordinated_list = []
    for color_name, color_code in color_dict.items():
        color_coordinated_list.append(f"\033[0;{color_code}m{color_name}\033[0m")
    final_formatted_string = " ".join(color_coordinated_list)
    print(f"Color Menu: {final_formatted_string}")


class ColorWheel:
    color_list = list(color_dictionary.values())

    def __init__(self):
        self.color_index = 0

    def arrows(self):
        color_arrow_string = ""
        arrow_option = "==> "
        for color in self.color_list:
            color_arrow_string = (
                color_arrow_string + f"\033[0;{color}m{arrow_option}\033[0m"
            )
        return color_arrow_string

    def alternate(self, input_text):
        remainder_int = self.color_index % len(self.color_list)
        color_code = self.color_list[remainder_int]
        color_formatted_text = f"\033[0;{color_code}m{input_text}\033[0m"
        self.color_index = self.color_index + 1
        return color_formatted_text


if __name__ == "__main__":
    print(cyan("\nTesting colors . . ."))
    color_object = ColorWheel()
    print("\n", color_object.arrows(), "\n")
