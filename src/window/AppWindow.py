import logging
import customtkinter as customtkinter

from src.window.States import FillerState, SageState, TableState, SettingsState
from src.window.StatesSwitcher import StateSwitcher
from src.handlers.settings_handlers import WindowSettingsHandler


class AppWindow(customtkinter.CTk):

    def __init__(self):
        super(AppWindow, self).__init__()
        self.window_settings_handler = WindowSettingsHandler("data/settings/window_settings.json")
        self.current_settings = self.window_settings_handler.get_current_settings()
        self.logger = logging.getLogger("app.main_window")

        self.state_switcher = StateSwitcher(
            states={
                "Наполнитель JSON'a": FillerState(master=self),
                "Перенос из Sage": SageState(master=self),
                "Перенос из таблицы": TableState(master=self),
                "Настройки": SettingsState(master=self)
            },
            start_state="Наполнитель JSON'a"
        )

        self.create_window()
        self.create_root_widgets()
        self.set_root_widgets()

        self.logger.debug(f"AppWindow was init")

    def create_window(self):
        self.title(self.current_settings.title)
        self.geometry(self.current_settings.window_geometry)
        self.minsize(
            self.current_settings.minsize_geometry[0],
            self.current_settings.minsize_geometry[1]
        )
        self.set_appearance_mode()
        customtkinter.set_default_color_theme(self.current_settings.themes.color_theme)

        self.logger.debug(f"""AppWindow create window with settings:
    title: {self.current_settings.title},
    geometry: {self.current_settings.window_geometry},
    minsize: {self.current_settings.minsize_geometry}""")

    def create_root_widgets(self):
        self.mod_button_var = customtkinter.StringVar(value="Наполнитель JSON'a")
        self.mod_button = customtkinter.CTkSegmentedButton(
            master=self,
            values=[
                "Наполнитель JSON'a",
                "Перенос из Sage",
                "Перенос из таблицы",
                "Настройки"
            ],
            command=self.state_switcher.set_new_state,
            variable=self.mod_button_var
        )

        self.columnconfigure(0, weight=1)

    def set_root_widgets(self):
        self.mod_button.grid(row=0, column=0, padx=20, pady=10, sticky="NEW", columnspan=1000)

    def set_appearance_mode(self) -> None:
        """Set appearance mod from settings"""
        customtkinter.set_appearance_mode(self.current_settings.themes.appearance_mode)
        self.logger.debug(f"Set appearance mod: '{self.current_settings.themes.appearance_mode}'")

    def switch_appearance_mod(self, mod: str) -> None:
        """Switch current appearance mod to opposite"""
        if mod == "Темная тема":
            customtkinter.set_appearance_mode("dark")
            self.logger.debug("Set appearance mod: 'dark'")
            self.window_settings_handler.set_new_settings(APPEARANCE_MOD='dark')
        elif mod == "Светлая тема":
            customtkinter.set_appearance_mode("light")
            self.logger.debug("Set appearance mod: 'light'")
            self.window_settings_handler.set_new_settings(APPEARANCE_MOD='light')
        else:
            raise Exception  # TODO Custom exception
