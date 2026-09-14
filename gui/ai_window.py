import aqt.qt
from PyQt6.QtGui import QTextLine
from PyQt6.QtWidgets import QGridLayout, QPushButton, QLabel, QVBoxLayout, QWidget
from aqt.browser import Browser
from aqt import mw
import anki

from ..utils.constants import AVAILABLE_MODELS, MODELS_INPUT_PRICES, MODELS_OUTPUT_PRICES


class ProfileConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Profile Configuration")
        self.resize(800, 600)
        self.setModal(False)
        self.setSizeGripEnabled(True)

        grid = aqt.qt.QGridLayout(self)
        grid.addLayout(PromptTextEditLayout(), 0, 0)
        grid.addLayout(ProfileCreationSettings(),0 ,1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)


class PromptTextEditLayout(aqt.qt.QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        prompt_label = aqt.qt.QLabel("Prompt")
        prompt_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        prompt_text_edit = aqt.qt.QPlainTextEdit()
        prompt_text_edit.setPlaceholderText("Enter your prompt here")
        prompt_text_edit.setToolTip("")  # TODO: Write a proper tool tip for prompt text edit

        self.addWidget(prompt_label, 0, 0)
        self.addWidget(prompt_text_edit, 1, 0)


class ProfileCreationSettings(aqt.qt.QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        # fields_tuple = ("Korean", "English", "Hanja", "Number", "Front", "Back", "Audio")

        self.addWidget(GenerationConfigLayout(), 0, 0)
        # self.addLayout(NoteFieldsCheckBoxes(fields_tuple=("Calculus Mathematical Equations", "Answer")), 0, 1)
        self.addWidget(SettingTabs(), 1, 0)


class GenerationConfigLayout(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        grid = QGridLayout(self)

        self.card_types_combo_box = CardTypesComboBox()
        self.note_fields_check_boxes = NoteFieldsCheckBoxes()
        self.on_card_type_selection()
        self.card_types_combo_box.currentIndexChanged.connect(self.on_card_type_selection)

        self.ai_models_combo_box = AiModelsComboBox()
        self.ai_model_prices = AiModelPricesLayout()
        self.on_model_selection()
        self.ai_models_combo_box.currentIndexChanged.connect(self.on_model_selection)

        grid.addWidget(self.card_types_combo_box, 0, 0)
        grid.addLayout(self.note_fields_check_boxes, 0, 1, 3, 1)
        grid.addWidget(self.ai_models_combo_box , 1, 0)
        grid.addLayout(self.ai_model_prices, 2, 0)

    def on_card_type_selection(self):
        card_type_str = str(self.card_types_combo_box.currentText())  # TODO Try to create an empty card type

        if card_type_str:
            card_type_id = mw.col.models.by_name(card_type_str)
            card_type_fields_list = mw.col.models.field_names(card_type_id)

            self.note_fields_check_boxes.create_field_check_boxes(card_type_fields_list)  # TODO Try to create card types with no fields

    def on_model_selection(self):
        model_name = str(self.ai_models_combo_box.currentText())
        self.ai_model_prices.set_input_price(MODELS_INPUT_PRICES[model_name])
        self.ai_model_prices.set_output_price(MODELS_OUTPUT_PRICES[model_name])


class CardTypesComboBox(aqt.qt.QComboBox):
    def __init__(self, parent: QWidget | None=None):
        super().__init__(parent)

        self.addItems(mw.col.models.all_names())
        self.setFixedWidth(200)


class NoteFieldsCheckBoxes(aqt.qt.QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.fields_check_boxes_widget = aqt.qt.QWidget()
        self.fields_check_boxes_vertical_layout = aqt.qt.QVBoxLayout(self.fields_check_boxes_widget)

        self.scroll_area = aqt.qt.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.fields_check_boxes_widget)

        self.scroll_area.setFixedHeight(180)
        # scroll_area.setMaximumHeight(180)

        self.addWidget(self.scroll_area)

    def create_field_check_boxes(self, fields_list):
        self.clear_field_check_boxes()

        for field in fields_list:
            check_box = aqt.qt.QCheckBox(str(field))
            check_box.setChecked(True)

            self.fields_check_boxes_vertical_layout.addWidget(check_box)

    def clear_field_check_boxes(self):
        while self.fields_check_boxes_vertical_layout.count():
            item = self.fields_check_boxes_vertical_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()


class AiModelsComboBox(aqt.qt.QComboBox):
    def __init__(self, parent: QWidget | None=None):
        super().__init__(parent)

        self.addItems(AVAILABLE_MODELS)
        self.setFixedWidth(200)


class AiModelPricesLayout(aqt.qt.QGridLayout):
    def __init__(self, parent: QWidget | None=None):
        super().__init__(parent)

        input_price_label = aqt.qt.QLabel("Input price:")
        input_price_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        output_price_label = aqt.qt.QLabel("Output price:")
        output_price_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        self.input_price_line = aqt.qt.QLineEdit()
        self.input_price_line.setReadOnly(True)
        self.input_price_line.setToolTip("Input Price for 1M tokens")  # TODO is tool tips good enough?

        self.output_price_line = aqt.qt.QLineEdit()
        self.output_price_line.setReadOnly(True)
        self.output_price_line.setToolTip("Output Price for 1M tokens")

        self.addWidget(input_price_label, 0, 0)
        self.addWidget(output_price_label, 0, 1)
        self.addWidget(self.input_price_line, 1, 0)
        self.addWidget(self.output_price_line, 1, 1)

    def set_input_price(self, input_price: float):
        self.input_price_line.setText(f"{input_price:.2f}$")

    def set_output_price(self, output_price: float):
        self.output_price_line.setText(f"{output_price:.2f}$")


class SettingTabs(aqt.qt.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        setting_widget = aqt.qt.QWidget()
        setting_layout = aqt.qt.QVBoxLayout(setting_widget)

        setting_button = aqt.qt.QPushButton("Settings button")
        setting_layout.addWidget(setting_button)

        self.addTab(ExpectedInputAndOutput(), "Expected Input and Output")  # TODO add expected output from AI text field
        self.addTab(setting_widget, "Settings")


class ExpectedInputAndOutput(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        field_layout = aqt.qt.QGridLayout(self)

        expected_input_label = aqt.qt.QLabel("Expected input for AI is:")  # # TODO Is label text good enough?
        expected_input_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        expected_output_label = aqt.qt.QLabel("Expected output from AI is:")
        expected_output_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        expected_fields_input_to_ai_text_edit = aqt.qt.QPlainTextEdit()
        expected_fields_input_to_ai_text_edit.setToolTip("This is how the input to AI will look like")  # TODO Is tooltip good enough?
        expected_fields_input_to_ai_text_edit.setReadOnly(True)

        expected_output_from_ai_text_edit = aqt.qt.QPlainTextEdit()
        expected_output_from_ai_text_edit.setToolTip("This is how the output from AI should look like")
        expected_output_from_ai_text_edit.setReadOnly(True)

        field_layout.addWidget(expected_input_label, 0, 0)
        field_layout.addWidget(expected_output_label, 0, 1)
        field_layout.addWidget(expected_fields_input_to_ai_text_edit, 1, 0)
        field_layout.addWidget(expected_output_from_ai_text_edit, 1, 1)


def open_configuration_dialog(browser: Browser):
    configuration_dialog = ProfileConfigurationDialog(browser)
    configuration_dialog.exec()

def test_function():
    aqt.utils.showInfo(str(mw.col.models.all_names()))