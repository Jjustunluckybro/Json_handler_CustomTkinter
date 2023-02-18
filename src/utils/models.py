from pydantic import BaseModel


# ---------- Models for filler settings ---------- #
class MonoPresetModel(BaseModel):
    name: str
    contact_id: str
    account_number: str
    contract_number: str
    product_type: str
    communication_type: str


class MonoDatesModel(BaseModel):
    date_1: int
    date_2: int
    date_3: int
    std: int


class MonoSettingsModel(BaseModel):
    presets: list[MonoPresetModel] = []
    dates: MonoDatesModel


class DoublePresetModel(BaseModel):
    name: str


class DoubleSettingsModel(BaseModel):
    presets: list[DoublePresetModel]
    dates: dict


class FillerSettingsModel(BaseModel):
    mono: MonoSettingsModel
    double: DoubleSettingsModel


# ---------- Models for window settings ---------- #
class Themes(BaseModel):
    appearance_mode: str
    color_theme: str


class WindowSettingsModel(BaseModel):
    title: str
    window_geometry: str
    minsize_geometry: list[int, int]
    themes: Themes
