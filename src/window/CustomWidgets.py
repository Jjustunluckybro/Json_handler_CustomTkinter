import tkinter

import customtkinter
from customtkinter import CTkFrame


class CustomInputBox(CTkFrame):
    w_label: customtkinter.CTkLabel
    text_box_var: customtkinter.StringVar
    w_text_box: customtkinter.CTkTextbox

    def __init__(self,
                 *args,
                 width: int = 100,
                 height: int = 32,
                 label_text: str,
                 text_box_text: str = "",
                 text_box_width: int = 150,
                 **kwargs):
        super(CustomInputBox, self).__init__(*args, width=width, height=height, **kwargs)
        self.label_text = label_text
        self.text_box_text = text_box_text
        self.text_box_width = text_box_width

        self.create_sub_widgets()
        self.set_sub_widgets()

    def create_sub_widgets(self):
        self.w_label = customtkinter.CTkLabel(master=self,
                                              text=self.label_text,
                                              padx=5,
                                              pady=5
                                              )

        self.w_text_box = customtkinter.CTkTextbox(master=self,
                                                   border_width=1,
                                                   height=28,
                                                   width=self.text_box_width,
                                                   padx=5,
                                                   pady=5
                                                   )

        # Пример раскараски определенного текста!!!
        # self.w_text_box.tag_config('tag_red_text', foreground='red')
        # self.w_text_box.insert(customtkinter.END, 'red text', 'tag_red_text')

    def set_sub_widgets(self):
        self.w_label.grid(column=0, row=0)
        self.w_text_box.grid(column=1, row=0)
        self.w_text_box.insert(customtkinter.INSERT, self.text_box_text)


class CustomSegmentBox(CTkFrame):
    w_segment_box: customtkinter.CTkSegmentedButton
    w_label: customtkinter.CTkLabel

    def __init__(self,
                 *args,
                 width: int = 100,
                 height: int = 32,
                 default_value: str,
                 mod_values: list,
                 label_text: str,
                 command,  # TODO: Need to type hint function
                 **kwargs):
        super(CustomSegmentBox, self).__init__(*args, width=width, height=height, **kwargs)
        self.label_text = label_text
        self.command = command
        self.mod_values = mod_values
        self.default_value = default_value

        self.create_sub_widgets()
        self.set_sub_widgets()

    def create_sub_widgets(self):
        self.w_label = customtkinter.CTkLabel(master=self,
                                              text=self.label_text,
                                              padx=5,
                                              pady=5
                                              )

        self.w_segment_box = customtkinter.CTkSegmentedButton(master=self,
                                                              values=self.mod_values,
                                                              command=self.command,
                                                              border_width=1
                                                              )

    def set_sub_widgets(self):
        self.w_label.grid(column=0, row=0)
        self.w_segment_box.grid(column=1, row=0)
        self.w_segment_box.set(self.default_value)


class CustomLabelCombobox(CTkFrame):

    def __init__(self,
                 *args,
                 width: int = 100,
                 height: int = 32,
                 label_text: str,
                 combobox_default_value: str,
                 combobox_values: list,
                 text_box_width: int = 150,
                 **kwargs) -> None:
        super(CustomLabelCombobox, self).__init__(*args, width=width, height=height, **kwargs)
        self.label_txt = label_text
        self.combobox_default_value = combobox_default_value
        self.combobox_values = combobox_values

        self.create_sub_widgets()
        self.set_sub_widgets()

    def create_sub_widgets(self) -> None:
        self.w_label = customtkinter.CTkLabel(master=self,
                                              text=self.label_txt,
                                              padx=5,
                                              pady=5)

        self.combobox_var = customtkinter.StringVar(value=self.combobox_default_value)
        self.w_combobox = customtkinter.CTkComboBox(master=self,
                                                    values=self.combobox_values,
                                                    variable=self.combobox_var,
                                                    justify="center")

    def set_sub_widgets(self) -> None:

        self.w_label.grid(column=0, row=0)
        self.w_combobox.grid(column=1, row=0)


class CustomSettingsBox(CTkFrame):

    def __init__(self,
                 *args,
                 width: int = 100,
                 height: int = 32,
                 text_box_width: int = 150,
                 **kwargs) -> None:
        super(CustomSettingsBox, self).__init__(*args, width=width, height=height, **kwargs)

    def create_all_widgets(self):

        self.settings_preset_box = CustomLabelCombobox(master=self,
                                                       label_text="Пресеты настроек:",
                                                       combobox_default_value="",
                                                       combobox_values=[""],
                                                       )
        self.save_settings_preset_btn = customtkinter.CTkButton(master=self,
                                                                text="Сохранить текущий пресет настроек",
                                                                command=self.callback_save_preset,
                                                                border_width=1)
        self.load_settings_preset_btn = customtkinter.CTkButton(master=self,
                                                                text="Загрузить выбранный пресет настроек",
                                                                command=self.callback_load_preset,
                                                                border_width=1)
        self.del_settings_preset_btn = customtkinter.CTkButton(master=self,
                                                               text="Удалить выбранный пресет настроек",
                                                               command=self.callback_delete_preset,
                                                               border_width=1,
                                                               fg_color="purple")

    def set_all_widgets(self):

        self.settings_preset_box.grid(row=0, column=0)

        self.save_settings_preset_btn.grid(column=0, row=1, sticky="EW")
        self.load_settings_preset_btn.grid(column=0, row=2, sticky="EW")
        self.del_settings_preset_btn.grid(column=0, row=3, sticky="EW")

    def callback_save_preset(self):
        raise NotImplementedError

    def callback_load_preset(self):
        raise NotImplementedError

    def callback_delete_preset(self):
        raise NotImplementedError

"""
Можно взять один json/ один хендлер настроек и просто по ключу mono/double их фильтровать
"""