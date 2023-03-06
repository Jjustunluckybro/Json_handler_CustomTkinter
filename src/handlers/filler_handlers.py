import datetime
import json
import logging

from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from src.utils.models import DatesModel, MonoDatesModel, MonoSettingsFromUIModel, DoubleSettingsFromUIModel
from src.utils.exceptions import ConvertStrToDictException

ROOT_JSON_PATH = "data/root_json.json"
DOUBLE_ROOT_JSON_PATH = "data/double_root_json.json"
SERVICE_JSON_PATH = "data/service_json.json"
logger = logging.getLogger("app.filler_handlers")


def plus_days_from_now(settings: MonoDatesModel = None) -> DatesModel:
    today = dt.today()

    date_1 = (today + datetime.timedelta(days=settings.date_1)).date()
    date_2 = (today + datetime.timedelta(days=settings.date_2)).date()
    date_3 = (today + datetime.timedelta(days=settings.date_3)).date()
    std = (today + datetime.timedelta(settings.std)).date()
    next_std = (std + relativedelta(months=1))

    return DatesModel(
        date_1=str(date_1),
        date_2=str(date_2),
        date_3=str(date_3),
        std=str(std),
        next_std=str(next_std)
    )


def filler(to_fill: str, from_fill: str, settings: MonoSettingsFromUIModel | DoubleSettingsFromUIModel) -> str:
    """

    :param to_fill: JSON in str format that will fill values from "from_fill" json
    :param from_fill: JSOn in str format. From this json will take values
    :param settings: Settings from UI
    :return: JSON in str format
    """

    logger.debug(f"Start filler"
                 f"|----| to_fill: {to_fill}"
                 f"|----| from_fill: {from_fill}")

    # Choose work mode
    is_mono: bool = isinstance(settings, MonoSettingsFromUIModel)
    logger.debug(f"Work mode 'is_mono': {is_mono}")

    # Prepare dict
    to_fill, from_fill = prepare_strings_to_filler(to_fill=to_fill, from_fill=from_fill, is_mono=is_mono)
    logger.debug(f"Dicts was prepare to fill")

    # Fill dict without use settings
    result: dict = fill_dict_from_another_dict(to_fill=to_fill, from_fill=from_fill)
    logger.debug(f"Fill dict without use settings, result: {result}")

    # Apply settings
    result: dict = apply_settings(result, settings)
    logger.debug(f"Apply settings and reform result dict: {result}")

    return correct_dict_to_export(result)


def fill_dict_from_another_dict(to_fill: dict, from_fill: dict) -> dict:
    logger.debug("Start filling dict from another dict")
    result = {}

    for key, value in to_fill.items():
        if key in from_fill:
            result[key] = from_fill[key]
        else:
            result[key] = to_fill[key]
    logger.debug("Finish filling dict from another dict")
    return result


def apply_settings(dict_to_valid: dict, settings: MonoSettingsFromUIModel | DoubleSettingsFromUIModel) -> dict:
    logger.debug(f"Start apply settings")
    # For mono
    if isinstance(settings, MonoSettingsFromUIModel):
        # logger.debug("Applying to mono")
        value_from_settings = {
            "PRODUCT_TYPE": settings.product_type,
            "PRIMARY_PRODUCT_TYPE": settings.product_type,
            "PRIMARY_ACCOUNT_PRODUCT_TYPE": settings.product_type,
            "CONTACT_ID": settings.contact_id,
            "ACCOUNT_NUMBER": settings.account_number,
            "PRIMARY_ACCOUNT_NUMBER": settings.account_number,
            "CONTRACT_NUMBER": settings.contract_number,
            "PRIMARY_CONTRACT_NUMBER": settings.contract_number,
            "COMMUNICATION_TYPE": settings.communication_type,
        }
        dates_value_from_settings = {
            "DATE1": settings.dates.date_1,
            "DATE_1": settings.dates.date_1,
            "PRIMARY_ACCOUNT_DATE1": settings.dates.date_1,
            "PRIMARY_ACCOUNT_DATE_1": settings.dates.date_1,
            "DATE2": settings.dates.date_2,
            "DATE_2": settings.dates.date_2,
            "PRIMARY_ACCOUNT_DATE2": settings.dates.date_2,
            "PRIMARY_ACCOUNT_DATE_2": settings.dates.date_2,
            "DATE3": settings.dates.date_3,
            "DATE_3": settings.dates.date_3,
            "PRIMARY_ACCOUNT_DATE3": settings.dates.date_3,
            "PRIMARY_ACCOUNT_DATE_3": settings.dates.date_3,
            "STD": settings.dates.std,
            "PRIMARY_ACCOUNT_STD": settings.dates.std,
            "NEXT_STD": settings.dates.next_std,
            "PRIMARY_ACCOUNT_NEXT_STD": settings.dates.next_std
        }
    # For Double
    else:
        value_from_settings = {}
        dates_value_from_settings = {}

    result_dict = {}
    for key, value in dict_to_valid.items():

        if (key in value_from_settings) and (value_from_settings[key] != "" or value_from_settings[key] != "\n"):
            result_dict[key] = value_from_settings.get(key)
            continue

        elif (key in dates_value_from_settings) and is_date_value(dates_value_from_settings[key]):
            result_dict[key] = dates_value_from_settings[key]
            continue

        elif settings.is_need_convert_dt and is_date_time_value(value):
            result_dict[key] = convert_dt_string_to_date(value)
            continue

        else:
            result_dict[key] = value
    logger.debug(f"Finish apply settings")

    return result_dict


def get_root_json_as_dict(is_for_mono: bool = True) -> dict:
    path = ROOT_JSON_PATH if is_for_mono else DOUBLE_ROOT_JSON_PATH
    with open(path, "r", encoding="utf-8") as file:
        root_json = json.load(file)
    logger.debug(f"Get root JSON:"
                 f"path: {path}"
                 f"root JSON: {root_json}")
    return root_json


def prepare_strings_to_filler(to_fill: str, from_fill: str, is_mono: bool) -> tuple[dict, dict]:
    if from_fill == "\n" or from_fill == "":
        from_fill = get_root_json_as_dict(is_for_mono=is_mono)
    else:
        try:
            from_fill: dict = json.loads(from_fill)
        except json.decoder.JSONDecodeError as err:
            raise ConvertStrToDictException(f"{str(err)}-F")

    try:
        to_fill: dict = json.loads(to_fill)
    except json.decoder.JSONDecodeError as err:
        raise ConvertStrToDictException(f"{str(err)}-T")

    logger.debug(f"Finish prepare json:"
                 f"to_fill: {to_fill} |----| type: {type(to_fill)}"
                 f"from_fill: {from_fill} |----| type: {type(from_fill)}")
    return to_fill, from_fill


def correct_dict_to_export(correcting_dict: dict) -> str:
    correcting_value = str(correcting_dict)
    correcting_value = correcting_value.replace("'", '"')
    correcting_value = correcting_value.replace("True", 'true')
    correcting_value = correcting_value.replace("False", 'false')
    correcting_value = correcting_value.replace("None", 'null')
    correcting_value = correcting_value.replace(',', ',\n')

    return correcting_value


def is_date_time_value(value) -> bool:
    """
    Check patter: %Y-%m-%dT%H:%M:%S.%f -> True;
    2022-11-28T08:25:47.123 -> True
    """
    try:
        dt.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def is_date_value(value) -> bool:
    """
    Check patter: %Y-%m-%d -> True;
    2022-11-28 -> True
    """
    try:
        dt.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def convert_dt_string_to_date(date_time: str) -> str:
    return str(dt.strptime(date_time, '%Y-%m-%dT%H:%M:%S.%f').date())


if __name__ == '__main__':
    ...
