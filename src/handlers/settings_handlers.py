import json
import logging

from pydantic import BaseModel

from src.utils.models import WindowSettingsModel, FillerSettingsModel, MonoPresetModel, DoublePresetModel
from src.utils.exceptions import PresetException


class SettingsHandler:
    _data: BaseModel

    def __init__(self, path: str):
        """
        :param path: path to JSON file
        """
        self._path = path

    def get_current_settings(self):
        answer = self._data.copy()
        return answer

    def _reed_json(self):
        """reed JSON file"""
        raise NotImplementedError

    def _write_to_json(self):
        """Write to JSON file"""
        raise NotImplementedError


class WindowSettingsHandler(SettingsHandler):
    _data: WindowSettingsModel

    def __init__(self, path: str):
        super(WindowSettingsHandler, self).__init__(path)
        self.logger = logging.getLogger('app.settings_handler.window_settings_handler')
        self._reed_json()

    def _reed_json(self):
        try:
            self._data = WindowSettingsModel.parse_file(self._path)
            self.logger.debug(f"Succsess reed file from directory: '{self._path}' and save as {self._data}")
        except FileNotFoundError as err:
            self.logger.error(f"No such file or directory: {self._path}")
            raise err

    def _write_to_json(self):
        try:
            with open(self._path, "w", encoding="utf-8") as file:
                json.dump(self._data.dict(), file, ensure_ascii=False, indent=2)
            self.logger.debug(f"Succsess write file: {self._data} to directory: {self._path}")
        except FileNotFoundError as err:
            self.logger.error(f"No such file or directory: {self._path}")
            raise err

    def set_new_settings(self, **kwargs):
        new_settings = self._data.dict()
        for key in kwargs:
            if key in self._data.dict():
                new_settings[key] = kwargs[key]
        self._data = WindowSettingsModel(**new_settings)
        self._write_to_json()

    def get_current_settings(self) -> WindowSettingsModel:
        answer = self._data.copy()
        return answer


class FillerSettingsHandler(SettingsHandler):
    _data: FillerSettingsModel

    def __init__(self, path: str):
        super(FillerSettingsHandler, self).__init__(path)
        self.logger = logging.getLogger("app.settings_handler.filler_settings_handler")
        self._reed_json()

    def _reed_json(self) -> None:
        try:
            self._data = FillerSettingsModel.parse_file(self._path)
            self.logger.debug(f"Succsess reed file from directory '{self._path}' and save as {self._data} ")
        except FileNotFoundError as err:
            self.logger.error(f"No such file or directory: {self._path}")
            raise err

    def _write_to_json(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as file:
                json.dump(self._data.dict(), file, ensure_ascii=False, indent=2)
            self.logger.debug(f"Succsess write file: {self._data} to directory: {self._path}")
        except FileNotFoundError as err:
            self.logger.error(f"No such file or directory: {self._path}")
            raise err

    def set_new_data_settings(self,
                              is_mono_settings: bool = True,
                              **kwargs) -> None:
        new_settings = self._data.mono.dict() if is_mono_settings else self._data.double.dict()

        for key in kwargs:
            if key in new_settings["dates"]:
                new_settings["dates"][key] = kwargs[key]
            else:
                raise KeyError(f"No key with name: {key}")

        if is_mono_settings:
            self._data.mono = self._data.mono.parse_obj(new_settings)
        else:
            self._data.double = self._data.double.parse_obj(new_settings)

        self._write_to_json()

    def add_new_preset(self, new_preset: MonoPresetModel | DoublePresetModel) -> None:
        """
        Add new preset to preset list.
        If preset with name already exits, then throw PresetException

        :param new_preset: new_preset: If type MonoPresetModel then write it to "mono" settings section |
            If type DoublePresetModel then write it to "double" settings section
        :return: None
        """
        # For mono
        if type(new_preset) is MonoPresetModel:
            preset_names = [prst.name for prst in self._data.mono.presets]
            if new_preset.name not in preset_names:
                self._data.mono.presets.append(new_preset)
                self.logger.debug(f"Add new preset '{new_preset}' to 'mono'")
            else:
                self.logger.error(f"Can't add new preset to 'mono': Preset with name: '{new_preset.name}' already exist")
                raise PresetException(f"Preset with name: '{new_preset.name}' already exist")
        # For double
        else:
            preset_names = [prst.name for prst in self._data.double.presets]
            if new_preset.name not in preset_names:
                self._data.double.presets.append(new_preset)
                self.logger.debug(f"Add new preset '{new_preset}' to 'double'")
            else:
                self.logger.error(
                    f"Can't add new preset to 'double': Preset with name: '{new_preset.name}' already exist")
                raise PresetException(f"Preset with name: '{new_preset.name}' already exist")

        self._write_to_json()

    def delete_preset_by_name(self, preset_name: str, is_from_mono: bool = True) -> None:
        """
        Delete preset by name from presets list
        If no preset with this name -> throw PresetException

        :param preset_name: Preset name to delete
        :param is_from_mono: True - try delete preset from "mono" settings,
            else try delete from "double" settings
        :return: None
        """

        is_delete_any_preset = False

        # For mono
        if is_from_mono:
            for i in range(0, len(self._data.mono.presets)):
                if self._data.mono.presets[i].name == preset_name:
                    self._data.mono.presets.pop(i)
                    is_delete_any_preset = True
                    break
        # For double
        else:
            for i in range(0, len(self._data.double.presets)):
                if self._data.double.presets[i].name == preset_name:
                    self._data.double.presets.pop(i)
                    is_delete_any_preset = True
                    break

        # Throw exception if no preset to delete
        if is_delete_any_preset:
            self._write_to_json()
            self.logger.debug(f"Delete new preset with name: {preset_name}")
        else:
            self.logger.error(f"Can't delete preset. No preset with name: {preset_name}")
            raise PresetException(f"No preset with name: '{preset_name}'")

    def get_all_presets_names(self, is_for_mono: bool = True) -> list:
        if is_for_mono:
            return [prst.name for prst in self._data.mono.presets]
        else:
            return [prst.name for prst in self._data.double.presets]

    def get_current_settings(self) -> FillerSettingsModel:
        self._reed_json()
        return self._data.copy()

    def get_preset_by_name(self, name, is_for_mono: bool = True) -> MonoPresetModel | DoublePresetModel:
        if is_for_mono:
            for preset in self._data.mono.presets:
                if name == preset.name:
                    return preset
        else:
            for preset in self._data.double.presets:
                if name == preset.name:
                    return preset
        raise PresetException(f"No preset with name: '{name}'")

if __name__ == '__main__':
    ...
