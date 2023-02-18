import logging
import customtkinter as customtkinter

from src.window.States import FillerState, SageState, TableState, SettingsState
from src.window.StatesSwitcher import StateSwitcher
from src.handlers.settings_handlers import WindowSettingsHandler


class AppWindow(customtkinter.CTk):

    def __init__(self):
        super(AppWindow, self).__init__()
        self.window_settings_handler = WindowSettingsHandler("data/settings/window_settings.json")
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
        self.title(self.window_settings_handler.current_settings.TITLE)
        self.geometry(self.window_settings_handler.current_settings.WINDOW_GEOMETRY)
        self.minsize(
            self.window_settings_handler.current_settings.MINSIZE_GEOMETRY[0],
            self.window_settings_handler.current_settings.MINSIZE_GEOMETRY[1]
        )
        self.set_appearance_mode()
        self.set_color_theme()

        self.logger.debug(f"""AppWindow create window with settings:
    title: {self.window_settings_handler.current_settings.TITLE},
    geometry: {self.window_settings_handler.current_settings.WINDOW_GEOMETRY},
    minsize: {self.window_settings_handler.current_settings.MINSIZE_GEOMETRY[0],
              self.window_settings_handler.current_settings.MINSIZE_GEOMETRY[1]}""")

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

    def set_appearance_mode(self, is_set_current_from_settings: bool = True) -> None:
        """
        :param is_set_current_from_settings: if True -> set from settings,
         else switch to opposite between "dark"\"light"
        :return: None
        """

        if not is_set_current_from_settings:
            if self.window_settings_handler.current_settings.APPEARANCE_MOD == "dark":
                self.window_settings_handler.set_new_settings(APPEARANCE_MOD="light")
            else:
                self.window_settings_handler.set_new_settings(APPEARANCE_MOD="dark")

        customtkinter.set_appearance_mode(self.window_settings_handler.current_settings.APPEARANCE_MOD)
        self.logger.debug(f"Set appearance mod: '{self.window_settings_handler.current_settings.APPEARANCE_MOD}'")

    def switch_appearance_mod(self, mod: str) -> None:
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

    def set_color_theme(self, is_set_current_from_settings: bool = True) -> None:
        # TODO: Need switcher or mby not?
        customtkinter.set_default_color_theme(self.window_settings_handler.current_settings.COLOR_THEME)

        self.logger.debug(f"Set color theme: {self.window_settings_handler.current_settings.COLOR_THEME}")
