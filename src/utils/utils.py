import json

from src.utils.exceptions import UnexpectedErrorMessage, ConvertStrToDictException
from src.utils.models import DecoderErrorLocation

ROOT_JSON_PATH = "data/root_json.json"
DOUBLE_ROOT_JSON_PATH = "data/double_root_json.json"


def parse_error_message(msg: str):
    """Invalid control character at: line 13 column 44 (char 432)-T"""

    # location = "1. 'В который переносим ключи'" if msg[-1] == "T" else "2. 'Из которого переносим ключ'и"
    match msg[-1]:
        case "T":
            location = "1. 'В который переносим ключи'"
        case "F":
            location = "2. 'Из которого переносим ключ'и"
        case _:
            location = ""

    line_index = msg.find("line") + 5
    column_index = msg.find("column") + 7
    char_index = msg.find("char ") + 5

    line = ''
    column = ''
    char = ''

    for symb in msg[line_index:]:
        if symb.isdigit():
            line += symb
        else:
            break

    for symb in msg[column_index:]:
        if symb.isdigit():
            column += symb
        else:
            break

    for symb in msg[char_index:]:
        if symb.isdigit():
            char += symb
        else:
            break

    try:
        return DecoderErrorLocation(
            location=location,
            line=int(line),
            column=int(column),
            char=int(char)
        )
    except ValueError as err:
        raise UnexpectedErrorMessage(f"This message text was not expected: {msg}, can't handel")


def correct_dict_to_export(correcting_dict: dict) -> str:
    correcting_value = str(correcting_dict)
    correcting_value = correcting_value.replace("'", '"')
    correcting_value = correcting_value.replace("True", 'true')
    correcting_value = correcting_value.replace("False", 'false')
    correcting_value = correcting_value.replace("None", 'null')
    correcting_value = correcting_value.replace(',', ',\n')

    return correcting_value


def convert_string_to_dict(string: str, error_endwith: str = "F") -> dict:
    try:
        return json.loads(string)
    except json.decoder.JSONDecodeError as err:
        raise ConvertStrToDictException(f"{str(err)}-{error_endwith}")


def get_root_json_as_dict(is_for_mono: bool = True) -> dict:
    path = ROOT_JSON_PATH if is_for_mono else DOUBLE_ROOT_JSON_PATH
    with open(path, "r", encoding="utf-8") as file:
        root_json = json.load(file)
    return root_json


def fix_dict_values_type(dictionary: dict, type_example: dict) -> dict:
    result = {}

    for k, v in dictionary.items():
        if k in type_example.keys():

            if v == "null":
                result[k] = None
                continue

            # Matching types
            if issubclass(type(type_example[k]), bool):
                result[k] = bool(v)

            elif issubclass(type(type_example[k]), int | float):
                try:
                    result[k] = int(v)
                except ValueError:
                    result[k] = float(v)

            elif issubclass(type(type_example[k]), str):
                result[k] = str(v)

            elif issubclass(type(type_example[k]), dict):
                # TODO: Need to convert string_to_convert to dict if it was nested json
                result[k] = v

            elif issubclass(type(type_example[k]), list):
                # TODO: Mapping empty list
                value_list = v.split(',')
                result[k] = [i.strip() for i in value_list]

            else:
                pass

    return result
