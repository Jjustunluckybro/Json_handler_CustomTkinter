import datetime
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from src.utils.models import DatesModel, MonoDatesModel


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


def fill_dict(to_fill: dict, from_fill: dict, settings) -> dict:
    ...
