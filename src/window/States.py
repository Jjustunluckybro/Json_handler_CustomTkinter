import logging

import customtkinter
import pydantic

from src.utils.exceptions import PresetException, ConvertStrToDictException, UnexpectedErrorMessage
from src.utils.models import FillerSettingsModel, MonoSettingsModel, MonoDatesModel, DatesModel, MonoPresetModel, \
    MonoSettingsFromUIModel, DecoderErrorLocation
from src.utils.utils import parse_error_message
from src.window.StatesSwitcher import State, StateSwitcher
from src.window.CustomWidgets import CustomInputBox, CustomSegmentBox, CustomLabelCombobox, CustomOutputWindow
from src.handlers.settings_handlers import FillerSettingsHandler, WindowSettingsHandler
from src.handlers.settings_handlers import FillerSettingsHandler
from src.handlers.filler_handlers import plus_days_from_now, filler

FILLER_SETTINGS_PATH = "data\settings\\filler_settings.json"


class FillerState(State):
    """
    State witch 3 active frames
    1. responsible for input\result
    2. Main activity like start, copy, delete
    3. Settings
    and feedback window
    """

    def __init__(self, master: customtkinter.CTkBaseClass):
        super(FillerState, self).__init__(master)
        self.settings_handler = FillerSettingsHandler("data/settings/filler_settings.json")

        # Get logger
        self.logger = logging.getLogger("app.states.filler_state")

        # Create and set state main frame
        self.create_frames()
        self.set_frames()

        # Create and set input_window_frame widgets
        self.create_input_windows_frame_widgets()
        self.set_input_windows_frame_widgets()

        # Init filler settings states
        self.sub_filler_settings_state_switcher = StateSwitcher(
            states={
                "Моно продукт": SubFillerMonoState(self.filler_settings_frame, self),
                "Дабл": SubFillerDoubleState(self.filler_settings_frame)
            },
            start_state="Моно продукт"
        )

    def set_state(self):
        self.set_frames()

        self.create_action_frame_widgets()
        self.set_action_frame_widgets()

        self.create_settings_filler_frame_widgets()
        self.set_settings_filler_frame_widgets()

    def remove_state(self):
        self.input_windows_frame.grid_remove()
        self.filler_settings_frame.grid_remove()
        self.feedback_window.grid_remove()

        all_action_widgets = self.action_frame.grid_slaves()
        for widget in all_action_widgets:
            widget.destroy()
        self.action_frame.grid_remove()

    # ----------- Widgets ----------- #
    def create_frames(self) -> None:
        """Create main frames whitch contain outher widgets"""
        self.input_windows_frame = customtkinter.CTkFrame(self.master)
        self.action_frame = customtkinter.CTkFrame(self.master)
        self.filler_settings_frame = customtkinter.CTkFrame(self.master)

        self.feedback_window = customtkinter.CTkTextbox(master=self.master,
                                                        width=1,
                                                        height=40,
                                                        )

    def set_frames(self) -> None:
        """Set main frame in app window"""
        self.input_windows_frame.grid(row=1, column=0, sticky="NEWS", padx=5, pady=5)
        self.action_frame.grid(row=2, column=0, sticky="NEWS", padx=5, pady=5)
        self.filler_settings_frame.grid(row=4, column=0, sticky="NEWS", padx=5, pady=5)

        # Set row\column configurate to AppWindow
        self.master.rowconfigure(1, weight=1)
        self.master.rowconfigure(4, weight=1)

        # Set row\column configurate to input_window_frame
        self.input_windows_frame.rowconfigure(1, weight=1)
        self.input_windows_frame.columnconfigure(0, weight=1)
        self.input_windows_frame.columnconfigure(1, weight=1)
        self.input_windows_frame.columnconfigure(2, weight=1)

        # Set row\column configurate to action_frame
        self.action_frame.rowconfigure(0, weight=1)
        for i in range(0, 8):
            self.action_frame.columnconfigure(i, weight=1)

        # Feedback window
        self.feedback_window.grid(row=3, column=0, sticky="EW", padx=5, pady=5)

    def create_input_windows_frame_widgets(self) -> None:
        """Create widgets which will be in input_window_frame"""

        # Labels
        self.label_textbox_l = customtkinter.CTkLabel(master=self.input_windows_frame,
                                                      text='1. JSON в который переносим ключи')
        self.label_textbox_m = customtkinter.CTkLabel(master=self.input_windows_frame,
                                                      text='2. JSON из которого переносим ключи')
        self.label_textbox_r = customtkinter.CTkLabel(master=self.input_windows_frame, text='Результат')

        # TextBoxes
        self.textbox_l = customtkinter.CTkTextbox(master=self.input_windows_frame,
                                                  width=300,
                                                  height=300,
                                                  border_width=1
                                                  )
        self.textbox_m = customtkinter.CTkTextbox(master=self.input_windows_frame,
                                                  width=300,
                                                  height=300,
                                                  border_width=1
                                                  )
        self.textbox_r = customtkinter.CTkTextbox(master=self.input_windows_frame,
                                                  width=300,
                                                  height=300,
                                                  border_width=1
                                                  )

    def set_input_windows_frame_widgets(self) -> None:
        """Set widgets in window_frame"""
        # Set Textbox
        self.textbox_l.grid(row=1, column=0, sticky="NSEW")
        self.textbox_m.grid(row=1, column=1, sticky="NSEW")
        self.textbox_r.grid(row=1, column=2, sticky="NSEW")

        # Set labels
        self.label_textbox_l.grid(row=0, column=0, sticky="NSEW")
        self.label_textbox_m.grid(row=0, column=1, sticky="NSEW")
        self.label_textbox_r.grid(row=0, column=2, sticky="NSEW")

    def create_action_frame_widgets(self) -> None:
        """Create widgets which will be in action_frame"""

        self.start_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Старт",
            command=self.start_btn_callback,
            border_width=1,
            fg_color="green"
        )
        self.copy_result_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Копировать результат",
            command=self.copy_result_btn_callback,
            border_width=1
        )
        self.clear_l_text_box_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Отчистить 1",
            command=self.clear_l_text_box_callback,
            border_width=1,
            fg_color="purple"
        )
        self.clear_m_text_box_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Отчистить 2",
            command=self.clear_m_text_box_callback,
            border_width=1,
            fg_color="purple"
        )
        self.clear_r_text_box_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Отчистить результат",
            command=self.clear_r_text_box_callback,
            border_width=1,
            fg_color="purple"
        )

    def set_action_frame_widgets(self) -> None:
        """Set widgets in action_frame"""
        self.start_btn.grid(row=0, column=0, sticky="NSWE")
        self.copy_result_btn.grid(row=0, column=1, sticky="NSWE")
        self.clear_l_text_box_btn.grid(row=0, column=5, sticky="NSWE")
        self.clear_m_text_box_btn.grid(row=0, column=6, sticky="NSWE")
        self.clear_r_text_box_btn.grid(row=0, column=7, sticky="NSWE")

    def create_settings_filler_frame_widgets(self) -> None:
        self.filler_settings_state_segment_btn_var = customtkinter.StringVar(value="Моно продукт")
        self.filler_settings_state_mod_segment_btn = customtkinter.CTkSegmentedButton(
            master=self.filler_settings_frame,
            values=["Моно продукт", "Дабл"],
            command=self.sub_filler_settings_state_switcher.set_new_state,
            variable=self.filler_settings_state_segment_btn_var
        )

    def set_settings_filler_frame_widgets(self) -> None:
        self.filler_settings_state_mod_segment_btn.grid(row=0, column=0, padx=5, pady=5, sticky="NW")

    # ----------- Buttons callbacks  ----------- #
    def start_btn_callback(self):
        to_fill = self.textbox_l.get(0.0, customtkinter.END)
        from_fill = self.textbox_m.get(0.0, customtkinter.END)

        try:
            if self.sub_filler_settings_state_switcher.get_current_state_name() == "Моно продукт":
                state = self.sub_filler_settings_state_switcher.get_current_state()
                settings: SubFillerMonoState = state.reed_date_settings()

                result = filler(to_fill=to_fill, from_fill=from_fill, settings=settings)

                self.textbox_r.delete(0.0, customtkinter.END)
                self.textbox_r.insert(0.0, customtkinter.END)
            else:
                self.set_feedback("Для даблов расчет пока не реализован, вернись на настройки 'Моно продукта'")
                return None

            self.textbox_r.delete(0.0, customtkinter.END)
            self.textbox_r.insert(0.0, result)
        except ConvertStrToDictException as err:
            try:
                err_location = parse_error_message(str(err))
                self.set_error_feedback(err_location)
            except UnexpectedErrorMessage as err:
                self.logger.error(str(err))




    def copy_result_btn_callback(self):
        ...

    def clear_l_text_box_callback(self):
        ...

    def clear_m_text_box_callback(self):
        ...

    def clear_r_text_box_callback(self):
        ...

    # -----------  ----------- #
    def set_feedback(self, text: str) -> None:
        self.feedback_window.delete(0.0, customtkinter.END)
        self.feedback_window.insert(customtkinter.INSERT, text)

    def set_error_feedback(self, err_location: DecoderErrorLocation) -> None:
        msg_feedback = f"Неверный синтаксис JSON'а {err_location.location}," \
                       f" Строка: {err_location.line}; Символ: {err_location.column}"
        self.set_feedback(msg_feedback)

        if err_location.location == "from_fill":
            str_with_error = self.textbox_l.get(0.0, customtkinter.END)
            print(str_with_error)
            self.textbox_l.tag_config('tag_red_text', foreground='red')
        else:
            str_with_error = self.textbox_m.get(0.0, customtkinter.END)
            self.textbox_m.tag_config('tag_red_text', foreground='red')



class SageState(State):

    def __init__(self, master: customtkinter.CTkBaseClass):
        super(SageState, self).__init__(master)
        self.root_frame = customtkinter.CTkFrame(master=master)
        self.action_frame = customtkinter.CTkFrame(master=master)
        self.create_widgets()

    def set_state(self):
        self.root_frame.grid(row=1, column=0, sticky="NEWS")
        self.action_frame.grid(row=2, column=0, sticky="NSWE")
        self.set_widgets()

    def remove_state(self):
        for widget in self.root_frame.slaves():
            widget.grid_remove()
        self.action_frame.grid_remove()
        self.root_frame.grid_remove()

    def create_widgets(self):
        # Labels
        self.label_textbox_l = customtkinter.CTkLabel(master=self.root_frame,
                                                      text='Строка из Sage,\nкоторую нужно конвертировать')
        self.label_textbox_m = customtkinter.CTkLabel(master=self.root_frame,
                                                      text="Пример JSON'a к которому нужно привести")
        self.label_textbox_r = customtkinter.CTkLabel(master=self.root_frame, text='Результат')

        # TextBoxes
        self.textbox_l = customtkinter.CTkTextbox(master=self.root_frame,
                                                  width=300,
                                                  height=300,
                                                  border_width=1
                                                  )
        self.textbox_m = customtkinter.CTkTextbox(master=self.root_frame,
                                                  width=300,
                                                  height=300,
                                                  border_width=1
                                                  )
        self.textbox_r = customtkinter.CTkTextbox(master=self.root_frame,
                                                  width=300,
                                                  height=300,
                                                  border_width=1
                                                  )

        # Buttons
        self.start_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Старт",
            command=self.start_btn_callback,
            border_width=1,
            fg_color="green"
        )
        self.copy_result_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Копировать результат",
            command=self.copy_result_btn_callback,
            border_width=1
        )
        self.clear_l_text_box_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Отчистить 1",
            command=self.clear_l_text_box_callback,
            border_width=1,
            fg_color="purple"
        )
        self.clear_m_text_box_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Отчистить 2",
            command=self.clear_m_text_box_callback,
            border_width=1,
            fg_color="purple"
        )
        self.clear_r_text_box_btn = customtkinter.CTkButton(
            master=self.action_frame,
            text="Отчистить результат",
            command=self.clear_r_text_box_callback,
            border_width=1,
            fg_color="purple"
        )

    def set_widgets(self):
        # Set Textbox
        self.textbox_l.grid(row=1, column=0, sticky="NSEW")
        self.textbox_m.grid(row=1, column=1, sticky="NSEW")
        self.textbox_r.grid(row=1, column=2, sticky="NSEW")

        # Set labels
        self.label_textbox_l.grid(row=0, column=0, sticky="NSEW")
        self.label_textbox_m.grid(row=0, column=1, sticky="NSEW")
        self.label_textbox_r.grid(row=0, column=2, sticky="NSEW")

        # Buttons
        self.start_btn.grid(row=0, column=0, sticky="NSWE")
        self.copy_result_btn.grid(row=0, column=1, sticky="NSWE")
        self.clear_l_text_box_btn.grid(row=0, column=5, sticky="NSWE")
        self.clear_m_text_box_btn.grid(row=0, column=6, sticky="NSWE")
        self.clear_r_text_box_btn.grid(row=0, column=7, sticky="NSWE")

    # ----------- Buttons callbacks  ----------- #
    def start_btn_callback(self):
        ...

    def copy_result_btn_callback(self):
        ...

    def clear_l_text_box_callback(self):
        ...

    def clear_m_text_box_callback(self):
        ...

    def clear_r_text_box_callback(self):
        ...


class TableState(State):

    def __init__(self, master: customtkinter.CTkBaseClass):
        super(TableState, self).__init__(master)

    def set_state(self): ...

    def remove_state(self): ...


class SubSettingsGeneralState(State):
    """App general settings"""
    root_frame: customtkinter.CTkFrame
    window_resolution_input_box: CustomInputBox

    def __init__(self, master: customtkinter.CTkBaseClass, window_settings: WindowSettingsHandler, main_window):
        super(SubSettingsGeneralState, self).__init__(master)
        self.root_frame = customtkinter.CTkFrame(master=self.master)
        self.settings_handler = window_settings
        self.main_window = main_window

    def set_state(self):
        self.create_all_widgets()
        self.set_all_widgets()

    def remove_state(self):
        all_widgets = self.root_frame.grid_slaves()
        for i in all_widgets:
            i.destroy()
        self.root_frame.grid_remove()

    def create_all_widgets(self):
        settings = self.settings_handler.get_current_settings()

        self.window_resolution_input_box = CustomInputBox(
            master=self.root_frame,
            label_text="Разрешение окна\nпри старте приложения:",
            text_box_text=settings.window_geometry,
            text_box_width=100
        )

        self.window_min_resolution_input_box = CustomInputBox(
            master=self.root_frame,
            label_text="       Минимальное       \n      разрешение окна:       ",  # TODO: Kludge with spaces!
            text_box_text=str(settings.minsize_geometry),
            text_box_width=100
        )

        default_value = 'Темная тема' if settings.themes.appearance_mode == 'dark' else 'Светлая тема'
        self.apperance_mod_switcher = CustomSegmentBox(
            master=self.root_frame,
            default_value=default_value,
            mod_values=["Темная тема", "Светлая тема"],
            label_text="    Тема:    ",
            command=self.main_window.switch_appearance_mod
        )

    def set_all_widgets(self):
        self.root_frame.grid(row=1, column=0, padx=20, pady=10, sticky="NEWS")

        self.window_resolution_input_box.grid(row=0, column=0, padx=5, pady=5, sticky="NEWS")
        self.window_min_resolution_input_box.grid(row=1, column=0, padx=5, pady=5, sticky="NEWS")
        self.apperance_mod_switcher.grid(row=2, column=0, padx=5, pady=5, sticky="NEWS")

    def delete_all_widgets(self): ...

    def callback_save_settings(self):
        """"""
        # TODO: get settings from window
        self.settings_handler.set_new_settings()


class SubSettingsFillerState(State):
    """Settings for filler mono/double"""

    def __init__(self, master: customtkinter.CTkBaseClass):
        super(SubSettingsFillerState, self).__init__(master)
        self.root_frame = customtkinter.CTkFrame(master=self.master)
        self.settings_handler = FillerSettingsHandler(FILLER_SETTINGS_PATH)

    def set_state(self):
        self.create_all_widgets()
        self.set_all_widgets()

    def remove_state(self):
        all_widgets = self.root_frame.grid_slaves()
        for i in all_widgets:
            i.destroy()
        self.root_frame.grid_remove()

    def create_all_widgets(self):
        # Labels
        self.mono_labal = customtkinter.CTkLabel(master=self.root_frame, text="Настройки 'Моно'")

        # Input Boxes
        self.date_1 = CustomInputBox(master=self.root_frame, label_text="DATE_1:")
        self.date_2 = CustomInputBox(master=self.root_frame, label_text="DATE_2:")
        self.date_3 = CustomInputBox(master=self.root_frame, label_text="DATE_3:")
        self.std = CustomInputBox(master=self.root_frame, label_text="   STD:   ")

        # Buttons
        self.save_mono_button = customtkinter.CTkButton(master=self.root_frame,
                                                        text="Сохранить настройки",
                                                        command=self.callback_save_settings,
                                                        border_width=1)

    def set_all_widgets(self):
        self.root_frame.grid(row=1, column=0, sticky="NEWS", padx=20, pady=10)

        # Mono
        # Labels
        self.mono_labal.grid(row=0, column=0)

        # Input boxes
        self.date_1.grid(row=1, column=0)
        self.date_2.grid(row=2, column=0)
        self.date_3.grid(row=3, column=0)
        self.std.grid(row=4, column=0)
        self.fill_input_boxes_from_settings()

        # Buttons
        self.save_mono_button.grid(row=5, column=0)

    def callback_save_settings(self):
        settings_from_ui = self.get_settings_from_ui()
        self.settings_handler.set_new_data_settings(**settings_from_ui.dict())

    def fill_input_boxes_from_settings(self) -> None:
        settings = self.get_mono_date_settings()
        self.date_1.set_new_text(str(settings.date_1))
        self.date_2.set_new_text(str(settings.date_2))
        self.date_3.set_new_text(str(settings.date_3))
        self.std.set_new_text(str(settings.std))

    def get_mono_date_settings(self) -> MonoDatesModel:
        return self.settings_handler.get_current_settings().mono.dates

    def get_settings_from_ui(self) -> MonoDatesModel:
        try:
            return MonoDatesModel(
                date_1=int(self.date_1.get_text()),
                date_2=int(self.date_2.get_text()),
                date_3=int(self.date_3.get_text()),
                std=int(self.std.get_text()),
            )
        except TypeError as err:
            raise err


class SettingsState(State):
    mod_button_var: customtkinter.StringVar
    mod_button: customtkinter.CTkSegmentedButton

    def __init__(self, master: customtkinter.CTkBaseClass):
        super(SettingsState, self).__init__(master)

        self.window_settings_handler = WindowSettingsHandler("data/settings/window_settings.json")
        self.root_frame = customtkinter.CTkFrame(master=self.master)
        self.main_window = master

        self.sub_settings_state_switcher = StateSwitcher(
            states={
                "Основные настройки": SubSettingsGeneralState(self.root_frame,
                                                              self.window_settings_handler,
                                                              main_window=self.master),
                'Настройки "наполнителя"': SubSettingsFillerState(self.root_frame)
            },
            start_state='Основные настройки'
        )

        self.create_all_widgets()

    def set_state(self):
        self.root_frame.grid(row=1, column=0, padx=20, pady=10, sticky="NEWS", )
        self.mod_button.grid(row=0, column=0, padx=20, pady=10, sticky="NEWS", columnspan=1000)
        self.root_frame.columnconfigure(0, weight=1)

    def remove_state(self):
        self.root_frame.grid_remove()

    def create_all_widgets(self):
        self.mod_button_var = customtkinter.StringVar(value="Основные настройки")
        self.mod_button = customtkinter.CTkSegmentedButton(
            master=self.root_frame,
            values=[
                "Основные настройки",
                'Настройки "наполнителя"'
            ],
            command=self.sub_settings_state_switcher.set_new_state,
            variable=self.mod_button_var
        )

    def set_all_widgets(self): ...

    def test_command(self, string):
        print(string)


class SubFillerMonoState(State):

    def __init__(self, master: customtkinter.CTkFrame, master_state: FillerState):
        super(SubFillerMonoState, self).__init__(master)
        self.root_frame = customtkinter.CTkFrame(master=master)
        self.settings_handler = FillerSettingsHandler(FILLER_SETTINGS_PATH)
        self.master_state = master_state

    def set_state(self) -> None:
        self.root_frame.grid(row=1, column=0, sticky="NEWS")
        self.create_all_widgets()
        self.set_all_widgets()

    def remove_state(self) -> None:
        self.root_frame.grid_remove()

    def create_all_widgets(self) -> None:
        # ComboBoxes
        self.contact_id_box = CustomLabelCombobox(master=self.root_frame,
                                                  label_text="           CONTACT_ID:           ",
                                                  combobox_default_value="",
                                                  combobox_values=[""]
                                                  )
        # print(self.master.winfo_visual())
        self.account_number_box = CustomLabelCombobox(master=self.root_frame,
                                                      label_text="     ACCOUNT_NUMBER:    ",
                                                      combobox_default_value="",
                                                      combobox_values=[""]
                                                      )
        self.contract_number_box = CustomLabelCombobox(master=self.root_frame,
                                                       label_text="   CONTRACT_NUMBER:   ",
                                                       combobox_default_value="",
                                                       combobox_values=[""]
                                                       )
        self.product_type_box = CustomLabelCombobox(master=self.root_frame,
                                                    label_text="         PRODUCT_TYPE:       ",
                                                    combobox_default_value="Common",
                                                    combobox_values=["Common", "Kvk", "Kbk"]
                                                    )
        self.communication_type_box = CustomLabelCombobox(master=self.root_frame,
                                                          label_text="COMMUNICATION_TYPE:",
                                                          combobox_default_value="Call",
                                                          combobox_values=["Call", "Chat"],
                                                          )

        presets_names = self.settings_handler.get_all_presets_names()
        default_value = presets_names[0] if len(presets_names) > 0 else ""
        self.settings_preset_box = CustomLabelCombobox(master=self.root_frame,
                                                       label_text="Пресеты настроек:",
                                                       combobox_default_value=default_value,
                                                       combobox_values=presets_names,
                                                       )

        # InputBoxes
        self.date1_input_box = CustomInputBox(master=self.root_frame,
                                              label_text="    Date 1:  ")
        self.date2_input_box = CustomInputBox(master=self.root_frame,
                                              label_text="    Date 2:  ")
        self.date3_input_box = CustomInputBox(master=self.root_frame,
                                              label_text="    Date 3:  ")
        self.std_input_box = CustomInputBox(master=self.root_frame,
                                            label_text="     STD:     ")
        self.next_std_input_box = CustomInputBox(master=self.root_frame,
                                                 label_text="Next STD:")

        # Buttons
        self.save_settings_preset_btn = customtkinter.CTkButton(master=self.root_frame,
                                                                text="Сохранить текущий пресет настроек",
                                                                command=self.callback_save_settings_preset,
                                                                border_width=1)
        self.load_settings_preset_btn = customtkinter.CTkButton(master=self.root_frame,
                                                                text="Загрузить выбранный пресет настроек",
                                                                command=self.callback_load_settings_preset,
                                                                border_width=1)
        self.del_settings_preset_btn = customtkinter.CTkButton(master=self.root_frame,
                                                               text="Удалить выбранный пресет настроек",
                                                               command=self.callback_del_settings_preset,
                                                               border_width=1,
                                                               fg_color="purple")
        self.calculate_dates = customtkinter.CTkButton(master=self.root_frame,
                                                       text=" Рассчитать даты ",
                                                       command=self.callback_calculate_datas,
                                                       border_width=1)

        # Checkbox
        self.format_date_chkbox_var = customtkinter.IntVar(value=1)
        self.format_date_chkbox = customtkinter.CTkCheckBox(master=self.root_frame,
                                                            text=" - Форматировать D&T в Data  ",
                                                            variable=self.format_date_chkbox_var)

    def set_all_widgets(self) -> None:
        # ComboBoxes
        self.contact_id_box.grid(row=0, column=0, sticky="WE")
        self.account_number_box.grid(row=1, column=0, sticky="WE")
        self.contract_number_box.grid(row=2, column=0, sticky="WE")
        self.product_type_box.grid(row=3, column=0, sticky="WE")
        self.communication_type_box.grid(row=4, column=0, sticky="WE")

        self.settings_preset_box.grid(row=0, column=1)

        # InputBoxes
        self.date1_input_box.grid(column=2, row=0, padx=1, pady=1, sticky="WE")
        self.date2_input_box.grid(column=2, row=1, padx=1, pady=1, sticky="WE")
        self.date3_input_box.grid(column=2, row=2, padx=1, pady=1, sticky="WE")
        self.std_input_box.grid(column=2, row=3, padx=1, pady=1, sticky="WE")
        self.next_std_input_box.grid(column=2, row=4, padx=1, pady=1, sticky="WE")

        # Buttons
        self.calculate_dates.grid(column=3, row=1)

        self.save_settings_preset_btn.grid(column=1, row=1, sticky="EW")
        self.load_settings_preset_btn.grid(column=1, row=2, sticky="EW")
        self.del_settings_preset_btn.grid(column=1, row=3, sticky="EW")

        # CheckBoxes
        self.format_date_chkbox.grid(column=3, row=0)

    # ----------- Settings ----------- #
    def get_settings(self) -> MonoSettingsModel:
        """Get settings from settings handler"""
        return self.settings_handler.get_current_settings().mono

    def reed_date_settings(self) -> MonoSettingsFromUIModel:
        """Reed settings from UI"""
        x = MonoSettingsFromUIModel(
            dates=DatesModel(
                date_1=self.date1_input_box.get_text().strip(),
                date_2=self.date2_input_box.get_text().strip(),
                date_3=self.date3_input_box.get_text().strip(),
                std=self.std_input_box.get_text().strip(),
                next_std=self.next_std_input_box.get_text().strip(),
            ),
            contact_id=self.contact_id_box.get_text().strip(),
            account_number=self.account_number_box.get_text().strip(),
            contract_number=self.contract_number_box.get_text().strip(),
            product_type=self.product_type_box.get_text().strip(),
            communication_type=self.communication_type_box.get_text().strip(),
            is_need_convert_dt=bool(self.format_date_chkbox_var.get())
        )

        print(x.is_need_convert_dt)
        return x

    def write_date_settings(self,
                            date_1: str = "",
                            date_2: str = "",
                            date_3: str = "",
                            std: str = "",
                            next_std: str = ""
                            ) -> None:
        """Set to UI date"""
        self.date1_input_box.set_new_text(date_1)
        self.date2_input_box.set_new_text(date_2)
        self.date3_input_box.set_new_text(date_3)
        self.std_input_box.set_new_text(std)
        self.next_std_input_box.set_new_text(next_std)

    # ----------- Callbacks ----------- #
    def callback_save_settings_preset(self):
        """Save preset into settings"""
        new_preset_name = self.settings_preset_box.get_text()
        new_preset = MonoPresetModel(
            name=new_preset_name,
            communication_type=self.communication_type_box.get_text(),
            product_type=self.product_type_box.get_text(),
            account_number=self.account_number_box.get_text(),
            contact_id=self.contact_id_box.get_text(),
            contract_number=self.contract_number_box.get_text()
        )
        try:
            self.settings_handler.add_new_preset(new_preset)
            self.settings_preset_box.add_new_value(new_preset_name)
            self.master_state.set_feedback(f"Save preset with name: '{new_preset_name}'")
        except PresetException as err:
            self.master_state.set_feedback(str(err))

    def callback_load_settings_preset(self):
        """Set preset by name from inputBox"""
        preset_name = self.settings_preset_box.get_text()
        try:
            preset = self.settings_handler.get_preset_by_name(preset_name)
            self.contact_id_box.set_new_text(preset.contact_id)
            self.account_number_box.set_new_text(preset.account_number)
            self.contract_number_box.set_new_text(preset.contract_number)
            self.product_type_box.set_new_text(preset.product_type)
            self.communication_type_box.set_new_text(preset.communication_type)
            self.master_state.set_feedback(f"Load preset with name: '{preset_name}'")
        except PresetException as err:
            self.master_state.set_feedback(str(err))

    def callback_del_settings_preset(self):
        """Delete preset from settings"""
        preset_name_to_del = self.settings_preset_box.get_text()
        try:
            self.settings_handler.delete_preset_by_name(preset_name_to_del)
            self.settings_preset_box.del_value(preset_name_to_del)
            self.master_state.set_feedback(f"Delete preset with name: '{preset_name_to_del}'")
        except PresetException as err:
            self.master_state.set_feedback(str(err))

    def callback_calculate_datas(self):
        """Calculates dates based on settings"""
        result = plus_days_from_now(self.get_settings().dates)
        self.write_date_settings(
            date_1=result.date_1,
            date_2=result.date_2,
            date_3=result.date_3,
            std=result.std,
            next_std=result.next_std,
        )


class SubFillerDoubleState(State):

    def __init__(self, master: customtkinter.CTkFrame):
        super(SubFillerDoubleState, self).__init__(master)

    def set_state(self) -> None: ...

    def remove_state(self) -> None: ...

    def create_all_widgets(self) -> None: ...

    def set_all_widgets(self) -> None: ...

    def get_settings(self): ...
