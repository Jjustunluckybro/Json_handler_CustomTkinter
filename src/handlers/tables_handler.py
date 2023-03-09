from logging import getLogger
from pandas import read_excel
from src.utils.utils import correct_dict_to_export, fix_dict_values_type

logger = getLogger("app.handlers.table")


def make_json_from_table(table_path: str, example_dict: dict) -> str:
    """

    :param table_path:
    :param example_dict:
    :return: JSON in string datetype
    """
    result_data = {}
    available_extensions = (".xlsx", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt")

    if 1 in [*map(lambda x: table_path.endswith(x), available_extensions)]:
        data = read_excel(open(table_path, "rb")).to_dict()
    else:
        raise ValueError("No support extension")

    try:
        variable_names: dict = data['variable_name']
        variable_values: dict = data['variable_value']
    except KeyError as err:
        logger.debug(f"Wrong structure, {data}")
        raise err

    for k in variable_names:
        result_data[variable_names[k]] = variable_values[k]

    result_data = fix_dict_values_type(result_data, example_dict)
    return correct_dict_to_export(result_data)
