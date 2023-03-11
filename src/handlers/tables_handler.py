from pandas import read_excel

from src.utils.exceptions import ConvertStrToDictException, NoSupportFileExtension
from src.utils.utils import correct_dict_to_export, fix_dict_values_type, convert_string_to_dict


def make_json_from_table(table_path: str, example_dict: dict | str) -> str:
    """

    :param table_path:
    :param example_dict:
    :return: JSON in string datetype
    """
    result_data = {}
    available_extensions = (".xlsx", ".xlsm", ".xlsb", ".odf", ".ods", ".odt")
    table_path = table_path.strip()

    if isinstance(example_dict, str):
        try:
            example_dict = convert_string_to_dict(example_dict)
        except ConvertStrToDictException as err:
            raise err

    if 1 in [*map(lambda x: table_path.endswith(x), available_extensions)]:
        try:
            data = read_excel(open(table_path, "rb")).to_dict()
        except FileNotFoundError as err:
            raise FileNotFoundError(table_path)
    else:
        raise NoSupportFileExtension(f"Available extensions: {available_extensions}")

    try:
        variable_names: dict = data['variable_name']
        variable_values: dict = data['variable_value']
    except KeyError as err:
        raise err

    for k in variable_names:
        result_data[variable_names[k]] = variable_values[k]

    result_data = fix_dict_values_type(result_data, example_dict)
    return correct_dict_to_export(result_data)
