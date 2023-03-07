import json

from filler_handlers import fill_dict_from_another_dict


def convert_sage_str_to_dict_with_correcting_types(sage_str: str, example_dict: dict) -> dict:
    """

    :param sage_str:
    :param example_dict:
    :return:
    """
    result: dict = {}

    result = convert_sage_vars_string_to_dict(sage_str)
    try:
        result = fix_dict_values_type(dictionary=result, type_example=example_dict)
    except ValueError as err:
        raise err  # TODO: handle err

    return result


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


if __name__ == '__main__':
    string_to_convert = """"""
    convert_sage_vars_string_to_dict(string=string_to_convert)