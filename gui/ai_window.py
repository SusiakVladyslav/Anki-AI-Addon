import aqt.qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextLine
from PyQt6.QtWidgets import QGridLayout, QPushButton, QLabel, QVBoxLayout, QWidget, QTableWidgetItem
from aqt.browser import Browser
from aqt import mw
import anki

from ..utils.constants import AVAILABLE_MODELS, MODELS_INPUT_PRICES, MODELS_OUTPUT_PRICES


class ProfileConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Profile Configuration")
        self.resize(1200, 800)
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

        self.generation_config = GenerationConfigLayout()
        self.settings_tabs = SettingTabs()

        self._update_expected_io_text_edits_on_fields_check_box_toggle()
        self._update_fields_setting_combo_box_on_fields_check_box_toggle()
        self._update_table_rows_on_fields_check_box_toggle()

        self._send_signal_of_initial_checkboxes_creation()

        self.addWidget(self.generation_config, 0, 0)
        self.addWidget(self.settings_tabs, 1, 0)

    def _send_signal_of_initial_checkboxes_creation(self):
        self.generation_config.note_fields_check_boxes.on_check_box_toggled()

    def _update_expected_io_text_edits_on_fields_check_box_toggle(self):
        self.generation_config.note_fields_check_boxes.fields_changed.connect(
            self.settings_tabs.expected_input_and_output.update_text_edits
        )

    def _update_fields_setting_combo_box_on_fields_check_box_toggle(self):
        self.generation_config.note_fields_check_boxes.fields_changed.connect(
            self.settings_tabs.profile_creation_tab.update_fields_setting_combo_box
        )

    def _update_table_rows_on_fields_check_box_toggle(self):
        self.generation_config.note_fields_check_boxes.fields_changed.connect(
            self.settings_tabs.profile_creation_tab.fields_settings_table.fill_field_name_columns
        )

        self.generation_config.note_fields_check_boxes.fields_changed.connect(
            self.settings_tabs.profile_creation_tab.fields_settings_table.fill_strip_columns_with_default_values
        )

    def _update_table_rows_on_fields_check_box_toggled(self):
        pass


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
        grid.addWidget(self.ai_models_combo_box, 1, 0)
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


class NoteFieldsCheckBoxes(aqt.qt.QVBoxLayout):
    fields_changed = aqt.qt.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.fields_check_boxes_widget = aqt.qt.QWidget()
        self.fields_check_boxes_vertical_layout = aqt.qt.QVBoxLayout(self.fields_check_boxes_widget)
        self.check_boxes_list = []
        self.fields_status = {}

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
            check_box.toggled.connect(self.on_check_box_toggled)

            self.fields_check_boxes_vertical_layout.addWidget(check_box)
            self.check_boxes_list.append(check_box)

        self.on_check_box_toggled()

    def clear_field_check_boxes(self):
        while self.fields_check_boxes_vertical_layout.count():
            item = self.fields_check_boxes_vertical_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()
        self.check_boxes_list.clear()

    def on_check_box_toggled(self):
        self.fields_status = {cb.text(): cb.isChecked() for cb in self.check_boxes_list}
        self.fields_changed.emit(self.fields_status)



class AiModelsComboBox(aqt.qt.QComboBox):
    def __init__(self, parent: QWidget | None=None):
        super().__init__(parent)

        self.addItems(AVAILABLE_MODELS)


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
        self.input_price_line.setText(decide_price_format(input_price) + "$")

    def set_output_price(self, output_price: float):
        self.output_price_line.setText(decide_price_format(output_price) + "$")


class SettingTabs(aqt.qt.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setting_widget = aqt.qt.QWidget()
        self.setting_layout = aqt.qt.QVBoxLayout(self.setting_widget)

        self.setting_button = aqt.qt.QPushButton("Settings button")
        self.setting_layout.addWidget(self.setting_button)

        self.expected_input_and_output = ExpectedInputAndOutput()
        self.profile_creation_tab = ProfileCreationTab()

        self.addTab(self.profile_creation_tab, "Profile creation")
        self.addTab(self.expected_input_and_output, "Expected Input and Output")
        self.addTab(self.setting_widget, "Settings")


class ExpectedInputAndOutput(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        field_layout = aqt.qt.QGridLayout(self)

        expected_input_label = aqt.qt.QLabel("Expected input for AI is:")  # # TODO Is label text good enough?
        expected_input_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        expected_output_label = aqt.qt.QLabel("Expected output from AI is:")
        expected_output_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        self.font = aqt.qt.QFont()
        self.font.setPointSize(12)

        self.expected_fields_input_to_ai_text_edit = aqt.qt.QPlainTextEdit()
        self.expected_fields_input_to_ai_text_edit.setToolTip("This is how the input to AI will look like")  # TODO Is tooltip good enough?
        self.expected_fields_input_to_ai_text_edit.setReadOnly(True)

        self.expected_output_from_ai_text_edit = aqt.qt.QPlainTextEdit()
        self.expected_output_from_ai_text_edit.setToolTip("This is how the output from AI should look like")
        self.expected_output_from_ai_text_edit.setReadOnly(True)

        self.expected_fields_input_to_ai_text_edit.setFont(self.font)
        self.expected_output_from_ai_text_edit.setFont(self.font)

        self.expected_fields_input_to_ai_text_edit.setLineWrapMode(
            aqt.qt.QPlainTextEdit.LineWrapMode.NoWrap
        )
        self.expected_fields_input_to_ai_text_edit.setHorizontalScrollBarPolicy(
            aqt.qt.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.expected_output_from_ai_text_edit.setLineWrapMode(
            aqt.qt.QPlainTextEdit.LineWrapMode.NoWrap
        )
        self.expected_output_from_ai_text_edit.setHorizontalScrollBarPolicy(
            aqt.qt.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        field_layout.addWidget(expected_input_label, 0, 0)
        field_layout.addWidget(expected_output_label, 0, 1)
        field_layout.addWidget(self.expected_fields_input_to_ai_text_edit, 1, 0)
        field_layout.addWidget(self.expected_output_from_ai_text_edit, 1, 1)

    def update_text_edits(self, fields_status: dict[str, bool]):
        selected_fields = [field for field, value in fields_status.items() if value]
        input_text = "".join(f"{field}|{{Field Data}}\n" for field in selected_fields)
        output_text = "".join(f"{field}|{{Generated Data}}\n" for field in selected_fields)

        self.expected_fields_input_to_ai_text_edit.setPlainText(input_text)
        self.expected_output_from_ai_text_edit.setPlainText(output_text)


class ProfileCreationTab(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        grid = aqt.qt.QGridLayout(self)

        self.fields_settings_table = FieldsSettingsTable()
        self.create_profile_button = aqt.qt.QPushButton("Create Profile")
        self.enter_profile_name_label = aqt.qt.QLabel("Enter profile name:")
        self.profile_name_line_edit = aqt.qt.QLineEdit()
        self.setting_for_individual_field_checkbox = aqt.qt.QCheckBox("Apply setting to individual fields")
        self.fields_setting_combo_box = FieldsSettingsComboBox()
        self.fields_settings = FieldsSettings()
        self.create_new_cards_checkbox = aqt.qt.QCheckBox("Create new cards from generated data")

        self.field_setting_combo_box_opacity_effect = aqt.qt.QGraphicsOpacityEffect(self.fields_setting_combo_box)
        self.fields_setting_combo_box.setGraphicsEffect(self.field_setting_combo_box_opacity_effect)
        self.fields_settings_table_opacity_effect = aqt.qt.QGraphicsOpacityEffect(self.fields_settings_table)
        self.fields_settings_table.setGraphicsEffect(self.fields_settings_table_opacity_effect)  # TODO can I create in a different method

        self.profile_name_line_edit.setToolTip("Enter Profile Name")
        self._add_function_for_individual_field_application_check_box_toggle()
        self._update_label_text_on_field_setting_text_change()

        grid.addWidget(self.setting_for_individual_field_checkbox, 0, 0, 1, 1, aqt.qt.Qt.AlignmentFlag.AlignBottom | aqt.qt.Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.fields_setting_combo_box, 1, 0, 1, 1, aqt.qt.Qt.AlignmentFlag.AlignTop | aqt.qt.Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.enter_profile_name_label, 2, 0, 1, 1, aqt.qt.Qt.AlignmentFlag.AlignBottom | aqt.qt.Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.profile_name_line_edit, 3, 0, 1, 1, aqt.qt.Qt.AlignmentFlag.AlignTop | aqt.qt.Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.fields_settings, 0, 1, 4, 1, aqt.qt.Qt.AlignmentFlag.AlignTop | aqt.qt.Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.fields_settings_table, 4, 0, 1, 2)
        grid.addWidget(self.create_profile_button, 5, 0, 1, 2)

        self._on_individual_field_application_check_box_toggle(False)

        self.fields_setting_combo_box.setFixedWidth(200)
        self.profile_name_line_edit.setFixedWidth(200)

        # grid.setRowStretch(4,4)

        self._set_widgets_height()

        self.fields_settings.fields_changed.connect(
            self.fields_settings_table.fill_strip_columns
        )

    def _on_individual_field_application_check_box_toggle(self, checked:bool):
        self.fields_setting_combo_box.setEnabled(checked)
        self.fields_settings_table.setEnabled(checked)

        if checked:
            self.field_setting_combo_box_opacity_effect.setOpacity(1.0)
            self.fields_settings_table_opacity_effect.setOpacity(1.0)
            current_field = self.fields_setting_combo_box.currentText()
            if current_field:
                self.fields_settings.clean_field_data()
                self.fields_settings.load_settings(current_field)
        else:
            self.field_setting_combo_box_opacity_effect.setOpacity(0.8)
            self.fields_settings_table_opacity_effect.setOpacity(0.8)
            self.fields_settings_table.clearSelection()
            self.fields_settings_table.fill_strip_columns_with_default_values()

            self.fields_settings.update_field_setting_labes_as_all_fields()
            self.fields_settings.clean_field_data()

    def _update_label_text_on_field_setting_text_change(self):
        self.fields_setting_combo_box.currentTextChanged.connect(
            self._on_field_setting_combo_box_changed
        )

    def _on_field_setting_combo_box_changed(self, new_field: str):
        if self.setting_for_individual_field_checkbox.isChecked() and new_field:
            self.fields_settings.load_settings(new_field)

    def _add_function_for_individual_field_application_check_box_toggle(self):
        self.setting_for_individual_field_checkbox.toggled.connect(
            self._on_individual_field_application_check_box_toggle
        )

    def _set_widgets_height(self):
        ITEM_HEIGHT = 20

        # Left side
        self.setting_for_individual_field_checkbox.setFixedHeight(ITEM_HEIGHT)
        self.fields_setting_combo_box.setFixedHeight(ITEM_HEIGHT)
        self.enter_profile_name_label.setFixedHeight(ITEM_HEIGHT)
        self.profile_name_line_edit.setFixedHeight(ITEM_HEIGHT)

        # Right side
        self.fields_settings.fields_setting_label.setFixedHeight(ITEM_HEIGHT)
        self.fields_settings.strip_html_check_box.setFixedHeight(ITEM_HEIGHT)
        self.fields_settings.strip_brackets_check_box.setFixedHeight(ITEM_HEIGHT)
        self.fields_settings.strip_non_ascii_check_box.setFixedHeight(ITEM_HEIGHT)


    def update_fields_setting_combo_box(self, fields_status: dict[str, bool]):
        self.fields_setting_combo_box.set_fields_to_combo_box(fields_status)
        self.fields_settings.clean_field_data()

    # def update_table_row_names_for_new_card_type(self, list_of_labels_names: list[str]):
    #     self.fields_settings_table.fill_field_name_column(list_of_labels_names)



class FieldsSettingsComboBox(aqt.qt.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_fields_to_combo_box(self, fields_status: dict[str, bool]) -> None:
        self.clear()

        selected_fields = [field for field, value in fields_status.items() if value]
        self.addItems(selected_fields)


class FieldsSettings(aqt.qt.QWidget):
    fields_changed = aqt.qt.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        v_layout = aqt.qt.QVBoxLayout(self)

        self._field_data: dict[str, dict[str, bool]] = {}
        self._current_field: str | None = None

        self.fields_setting_label = aqt.qt.QLabel("All Fields Settings:")
        self.strip_html_check_box = aqt.qt.QCheckBox("Strip HTML in fields")
        self.strip_brackets_check_box = aqt.qt.QCheckBox("Strip brackets in fields")
        self.strip_non_ascii_check_box = aqt.qt.QCheckBox("Strip non-ascii characters in fields")

        self.strip_html_check_box.toggled.connect(self._on_setting_change)
        self.strip_brackets_check_box.toggled.connect(self._on_setting_change)
        self.strip_non_ascii_check_box.toggled.connect(self._on_setting_change)

        v_layout.addWidget(self.fields_setting_label)
        v_layout.addWidget(self.strip_html_check_box)
        v_layout.addWidget(self.strip_brackets_check_box)
        v_layout.addWidget(self.strip_non_ascii_check_box)

        v_layout.setSpacing(12)

    def _on_setting_change(self):
        if not self._current_field:
            return

        self._field_data[self._current_field] = {
            "strip_html" : self.strip_html_check_box.isChecked(),
            "strip_brackets" : self.strip_brackets_check_box.isChecked(),
            "strip_non_ascii" : self.strip_non_ascii_check_box.isChecked()
        }

        self.fields_changed.emit(self._field_data)

    def load_settings(self, field_name: str):

        self._current_field = field_name
        self._update_field_setting_label_as_individual_field(field_name)

        default_settings = {
            "strip_html": False,
            "strip_brackets": False,
            "strip_non_ascii": False
        }

        settings = self._field_data.setdefault(field_name, default_settings)

        self._block_signals_to_check_boxes(True)

        self.strip_html_check_box.setChecked(settings["strip_html"])
        self.strip_brackets_check_box.setChecked(settings["strip_brackets"])
        self.strip_non_ascii_check_box.setChecked(settings["strip_non_ascii"])

        self._block_signals_to_check_boxes(False)

    def _update_field_setting_label_as_individual_field(self, selected_field):
        self.fields_setting_label.setText(f"{selected_field} Field Settings:")

    def _block_signals_to_check_boxes(self, state: bool):
        self.strip_html_check_box.blockSignals(state)
        self.strip_brackets_check_box.blockSignals(state)
        self.strip_non_ascii_check_box.blockSignals(state)

    def update_field_setting_labes_as_all_fields(self):  # TODO See where I can remove this function
        self.fields_setting_label.setText("All Fields Settings:")

    def clean_field_data(self):
        self._field_data.clear()

        self._block_signals_to_check_boxes(True)

        self.strip_html_check_box.setChecked(False)
        self.strip_brackets_check_box.setChecked(False)
        self.strip_non_ascii_check_box.setChecked(False)

        self._block_signals_to_check_boxes(False)


class FieldsSettingsTable(aqt.qt.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setEditTriggers(aqt.qt.QAbstractItemView.EditTrigger.NoEditTriggers)

        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Field Name', 'Strip HTML', 'Strip brackets', 'Strip non-ascii'])

        self.horizontalHeader().setSectionResizeMode(
            aqt.qt.QHeaderView.ResizeMode.Stretch
        )

        self.verticalHeader().hide()

    def fill_field_name_columns(self, fields_status: dict[str, bool]):
        selected_fields = [field for field, value in fields_status.items() if value]
        selected_fields_length = len(selected_fields)
        self.setRowCount(selected_fields_length)

        for row_index in range(selected_fields_length):
            self.setItem(row_index, 0, QTableWidgetItem(selected_fields[row_index]))

    def fill_strip_columns(self, field_data: dict[str, dict[str, bool]]):
        for row_index in range(self.rowCount()):
            field_name_cell = self.item(row_index, 0)
            field_name = field_name_cell.text() if field_name_cell else ""

            if field_name in field_data:
                field_settings = field_data[field_name]

                for col_index, strip_setting in enumerate(("strip_html", "strip_brackets", "strip_non_ascii"), start=1):
                    self.setItem(
                        row_index,
                        col_index,
                        create_table_check_item(checked=field_settings[strip_setting])
                    )


    def fill_strip_columns_with_default_values(self):
        for row_index in range(self.rowCount()):
            for col in (1, 2, 3):
                self.setItem(row_index, col, create_table_check_item(checked=False))


    def clean_strip_columns_values(self):
        for row_index in range(self.rowCount()):
            self.setItem(row_index, 1, QTableWidgetItem(""))
            self.setItem(row_index, 2, QTableWidgetItem(""))
            self.setItem(row_index, 3, QTableWidgetItem(""))


def open_configuration_dialog(browser: Browser) -> None:
    configuration_dialog = ProfileConfigurationDialog(browser)
    configuration_dialog.exec()


def decide_price_format(price: float) -> str:
    three_digits_after_decimal_point_price = f"{price:.3f}"
    if three_digits_after_decimal_point_price.endswith("0"):
        return f"{price:.2f}"

    return three_digits_after_decimal_point_price

def create_table_check_item(checked: bool) -> QTableWidgetItem:
    green = "#4CAF50"
    red = "#F44336"

    symbol = "✔" if checked else "✖"
    color = green if checked else red

    item = QTableWidgetItem(symbol)
    item.setForeground(aqt.qt.QColor(color))
    item.setTextAlignment(aqt.Qt.AlignmentFlag.AlignCenter)
    return item

def test_function():
    aqt.utils.showInfo(str(mw.col.models.all_names()))
