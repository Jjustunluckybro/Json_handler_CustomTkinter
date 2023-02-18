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
    presets: [MonoPresetModel]
    dates: MonoDatesModel
