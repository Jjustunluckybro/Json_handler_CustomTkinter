import json
import logging
from typing import NamedTuple


class WindowSettings(NamedTuple):
    TITLE: str
    WINDOW_GEOMETRY: str
    MINSIZE_GEOMETRY: tuple[int, int]
    APPEARANCE_MOD: str
    COLOR_THEME: str


class FillerSettings(NamedTuple):
    PRESETS: list
    DATES: dict


class SageSettings(NamedTuple):
    ...


class TableSettings(NamedTuple):
    ...


class SettingsHandler:
    _settings_dict: dict  # Settings JSON file as dict

    def __init__(self, path: str):
        self._path = path
        self._reed_settings()
        self._reed_settings_to_named_tuple()

    def _reed_settings(self):
        """
        Reed JSON file with settings and return it as dict
        Should be saved in var "settings_dict"
        """
        raise NotImplementedError

    def _reed_settings_to_named_tuple(self):
        """Write settings to self "current settings" named tuple"""
        raise NotImplementedError

    def _write_settings_to_json(self):
        """Write self current settings to json file"""
        raise NotImplementedError

    def set_new_settings(self, **kwargs):
        """Set new settings by NamedTuple names"""
        raise NotImplementedError


# class SettingsHandler2:
#
#     def set_new_settings(self, **kwargs):
#         ...
#
#     def get_current_settings(self):
#         ...


class WindowSettingsHandler(SettingsHandler):
    current_settings: WindowSettings

    def __init__(self, path: str):
        self.logger = logging.getLogger("app.settings_handler.window")
        super(WindowSettingsHandler, self).__init__(path)
        self.logger.debug("WindowSettingsHandler was init")

    def _reed_settings(self):
        with open(self._path, "r", encoding="utf-8") as file:
            self.settings_dict = json.load(file)
            self.logger.debug(f"Settings was reeded: {self.settings_dict}")

    def update_settings(self):
        self._reed_settings()
        self._reed_settings_to_named_tuple()

    def _reed_settings_to_named_tuple(self):
        try:
            minsize_list = self.settings_dict["minsize_geometry"].split("x")
            minsize = (int(minsize_list[0]), int(minsize_list[1]))
            self.logger.debug(f"Convert minsize geometry as x = {minsize[0]}, y = {minsize[1]}")

            self.current_settings = WindowSettings(
                WINDOW_GEOMETRY=self.settings_dict["window_geometry"],
                TITLE=self.settings_dict["title"],
                MINSIZE_GEOMETRY=minsize,
                APPEARANCE_MOD=self.settings_dict["themes"]["appearance_mode"],
                COLOR_THEME=self.settings_dict["themes"]["color_theme"]
            )

            self.logger.debug(f"""Settings was saved:
    Geometry: {self.current_settings.WINDOW_GEOMETRY}, type: {type(self.current_settings.WINDOW_GEOMETRY)}
    TITLE: {self.current_settings.TITLE}, type: {type(self.current_settings.TITLE)}
    MINSIZE_GEOMETRY: {self.current_settings.MINSIZE_GEOMETRY}, type: {type(
                self.current_settings.MINSIZE_GEOMETRY)}
    APPEARANCE_MOD: {self.current_settings.APPEARANCE_MOD}, type: {type(self.current_settings.APPEARANCE_MOD)}
    COLOR_THEME: {self.current_settings.COLOR_THEME}, type: {type(self.current_settings.COLOR_THEME)}""")

        except KeyError as err:
            self.logger.error(f"Can't save settings, not found key. Error: {err}")
            raise err

    def _write_settings_to_json(self):
        with open(self._path, "w", encoding="utf-8") as file:
            json.dump(self.settings_dict, file, ensure_ascii=False)
            self.logger.debug(f"Write {self.settings_dict} to settings")

    def _set_new_settings_dict_from_settings_namedtuple(self):
        minsize = f"{self.current_settings.MINSIZE_GEOMETRY[0]}x{self.current_settings.MINSIZE_GEOMETRY[1]}"

        try:
            self.settings_dict["title"] = self.current_settings.TITLE
            self.settings_dict["window_geometry"] = self.current_settings.WINDOW_GEOMETRY
            self.settings_dict["minsize_geometry"] = minsize
            self.settings_dict["themes"]["appearance_mode"] = self.current_settings.APPEARANCE_MOD
            self.settings_dict["themes"]["color_theme"] = self.current_settings.COLOR_THEME
        except KeyError as err:
            self.logger.error(f"Can not find key: {err}")
            raise err

    def set_new_settings(self, **kwargs):
        self.current_settings = WindowSettings(
            WINDOW_GEOMETRY=kwargs[
                "WINDOW_GEOMETRY"] if "WINDOW_GEOMETRY" in kwargs else self.current_settings.WINDOW_GEOMETRY,
            TITLE=kwargs["TITLE"] if "TITLE" in kwargs else self.current_settings.TITLE,
            MINSIZE_GEOMETRY=kwargs[
                "MINSIZE_GEOMETRY"] if "MINSIZE_GEOMETRY" in kwargs else self.current_settings.MINSIZE_GEOMETRY,
            APPEARANCE_MOD=kwargs[
                "APPEARANCE_MOD"] if "APPEARANCE_MOD" in kwargs else self.current_settings.APPEARANCE_MOD,
            COLOR_THEME=kwargs["COLOR_THEME"] if "COLOR_THEME" in kwargs else self.current_settings.COLOR_THEME,
        )

        self._set_new_settings_dict_from_settings_namedtuple()
        self._write_settings_to_json()
        self.logger.debug(f"Save and write new window settings: {self.current_settings}")


class FillerSettingsHandler(SettingsHandler):

    def __init__(self, path: str, mode: str):
        """
        :param path: path to JSON file
        :param mode: "mono" or "double"
        """
        super(FillerSettingsHandler, self).__init__(path)
        self._mode = mode
        self.logger = logging.getLogger("app.settings_handler.filler")
        self.logger.debug(f"FillerSettingsHandler was init with {self._mode} mode")

    def _reed_settings(self):
        with open(self._path, "r", encoding="utf-8") as f:
            try:
                self._settings_dict = json.load(f)
                self.logger.debug(f"Read filler_settings json: {self._settings_dict}")
                return self._settings_dict
            except Exception as err:
                self.logger.error(f"Can'not reed filler_settings JSON, path: {self._path}")
                raise err

    def _reed_settings_to_named_tuple(self):
        ...

    def _write_settings_to_json(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._settings_dict, f, ensure_ascii=False)

    def set_new_settings(self, **kwargs):
        ...

    def _set_settings_to_mono(self, **kwargs) -> dict:
        ...

    def _set_settings_to_double(self, **kwargs) -> dict:
        ...


class SageSettingsHandler(SettingsHandler):

    def __init__(self, path: str):
        super(SageSettingsHandler, self).__init__(path)

    def _reed_settings(self): ...

    def _reed_settings_to_named_tuple(self): ...

    def _write_settings_to_json(self): ...

    def set_new_settings(self, **kwargs): ...


class TableSettingsHandler(SettingsHandler):

    def __init__(self, path: str):
        super(TableSettingsHandler, self).__init__(path)

    def _reed_settings(self): ...

    def _reed_settings_to_named_tuple(self): ...

    def _write_settings_to_json(self): ...

    def set_new_settings(self, **kwargs): ...


if __name__ == '__main__':
    ...
