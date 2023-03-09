from src.utils.utils import correct_dict_to_export, fix_dict_values_type, get_root_json_as_dict, convert_string_to_dict
from src.utils.exceptions import ConvertStrToDictException


def convert_sage_str_to_dict_with_correcting_types(sage_str: str, example_dict: dict | str) -> str:
    """

    :param sage_str:
    :param example_dict:
    :return:
    """

    result = convert_sage_vars_string_to_dict(sage_str)

    if isinstance(example_dict, str) and example_dict.strip() == "":
        example_dict = get_root_json_as_dict()
    elif isinstance(example_dict, str):
        try:
            example_dict = convert_string_to_dict(example_dict)
        except ConvertStrToDictException as err:
            raise err

    try:
        result = fix_dict_values_type(dictionary=result, type_example=example_dict)
    except ValueError as err:
        raise err  # TODO: handle err

    return correct_dict_to_export(result)


def convert_sage_vars_string_to_dict(string: str):
    strings = []
    result = {}
    string = string.split('\n')

    for i in string:
        strip_string = i.strip()
        if len(strip_string):
            strings.append(strip_string)

    keys_and_values = []
    for i in strings:
        keys_and_values.append(i.split('='))

    for i in keys_and_values:
        result[i[0].strip()] = i[1].strip()

    return result
