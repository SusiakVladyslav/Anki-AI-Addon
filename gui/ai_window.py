import aqt.qt
from PyQt6.QtGui import QTextLine
from PyQt6.QtWidgets import QGridLayout, QPushButton, QLabel, QVBoxLayout, QWidget
from aqt.browser import Browser

class ProfileConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Profile Configuration")
        self.resize(800, 600)
        self.setModal(False)
        self.setSizeGripEnabled(True)

        prompt_text_edit = aqt.qt.QPlainTextEdit()
        prompt_text_edit.setPlaceholderText("Enter your prompt here")
        prompt_text_edit.setToolTip("")  # TODO: Write a proper tool tip for prompt text edit

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(prompt_text_edit, 0, 0)
        grid.addLayout(ProfileCreationSettings(),0 ,1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)


class ProfileCreationSettings(aqt.qt.QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.addLayout(NoteFieldsCheckBoxes(fields_tuple=("Korean", "English", "Hanja", "Number", "Front", "Back", "Audio")), 0, 1)

        tabs = aqt.qt.QTabWidget()

        field_widget = aqt.qt.QWidget()
        field_layout = aqt.qt.QVBoxLayout(field_widget)

        fields_output_text_edit = aqt.qt.QPlainTextEdit()
        fields_output_text_edit.setPlaceholderText("Field Output is:")

        field_layout.addWidget(fields_output_text_edit)

        setting_widget = aqt.qt.QWidget()
        setting_layout = aqt.qt.QVBoxLayout(setting_widget)

        setting_button = aqt.qt.QPushButton("Settings button")
        setting_layout.addWidget(setting_button)

        tabs.addTab(field_widget, "Field Output")  # TODO add expected output from AI text field
        tabs.addTab(setting_widget, "Settings")

        self.addLayout(GenerationConfigLayout(), 0, 0)
        self.addWidget(tabs, 1, 0, 1, 2)
        # self.addWidget(button3, 1, 1)

class GenerationConfigLayout(aqt.qt.QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.addLayout(NoteFieldsCheckBoxes(fields_list=["Korean", "English", "Hanja", "Number", "Front", "Back", "Audio"]), 0, 1)

        card_types_combo_box = CardTypesComboBox()
        ai_model_version = AiModelsComboBox()

        input_price_label = aqt.qt.QLabel("Input price:")
        output_price_label = aqt.qt.QLabel("Output price:")

        input_price_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)
        output_price_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        input_price_line = aqt.qt.QLineEdit()
        input_price_line.setText("5.00$")
        input_price_line.setReadOnly(True)
        input_price_line.setToolTip("Input Price for 1M tokens for model")

        output_price_line = aqt.qt.QLineEdit()
        output_price_line.setText("Output Price")
        output_price_line.setReadOnly(True)

        self.addWidget(card_types_combo_box, 0, 0, 1, 2)
        self.addWidget(ai_model_version, 1, 0, 1, 2)
        self.addWidget(input_price_label, 2, 0)
        self.addWidget(output_price_label, 2, 1)
        self.addWidget(input_price_line, 3, 0)
        self.addWidget(output_price_line, 3, 1)


class CardTypesComboBox(aqt.qt.QComboBox):
    def __init__(self, parent: QWidget | None=None, available_card_types: tuple[str] = tuple()):
        super().__init__(parent)

        self.addItems(available_card_types)
        self.setFixedWidth(200)


class AiModelsComboBox(aqt.qt.QComboBox):
    def __init__(self, parent: QWidget | None=None, models: tuple[str] = tuple()):
        super().__init__(parent)

        self.addItems(models)
        self.setFixedWidth(200)


class AiModelPrices(aqt.qt.QGridLayout):
    def __init__(self, parent: QWidget | None=None, input_price=0, output_price=0):
        super().__init__(parent)


class NoteFieldsCheckBoxes(aqt.qt.QVBoxLayout):
    def __init__(self, fields_tuple: tuple[str]=tuple()):
        super().__init__()

        fields_check_boxes_container = aqt.qt.QWidget()

        fields_check_boxes_vertical_layout = aqt.qt.QVBoxLayout(fields_check_boxes_container)


        for field in fields_tuple:
            check_box = aqt.qt.QCheckBox(str(field))
            check_box.setChecked(True)

            fields_check_boxes_vertical_layout.addWidget(check_box)

        scroll_area = aqt.qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(fields_check_boxes_container)

        scroll_area.setFixedHeight(180)
        # scroll_area.setMaximumHeight(180)

        self.addWidget(scroll_area)



def open_configuration_dialog(browser):
    configuration_dialog = ProfileConfigurationDialog(browser)
    configuration_dialog.exec()
