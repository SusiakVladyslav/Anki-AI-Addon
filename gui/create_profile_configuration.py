import aqt.qt
from aqt.browser import Browser
from aqt import mw

from ..utils.constants import AVAILABLE_MODELS, MODELS_INPUT_PRICES, MODELS_OUTPUT_PRICES


class ProfileConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Profile Configuration")
        self.resize(1200, 800)
        self.setModal(False)
        self.setSizeGripEnabled(True)

        self.prompt_text_edit = PromptTextEditLayout()
        self.profile_creation_settings = ProfileCreationSettings()

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(self.prompt_text_edit, 0, 0)
        grid.addLayout(self.profile_creation_settings,0 ,1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.profile_creation_settings.create_profile_button.clicked.connect(self.get_profile_creation_settings)

    def get_profile_creation_settings(self):
        setting_for_created_profile_dict = dict()
        setting_for_created_profile_dict["prompt_text"] = self.prompt_text_edit.prompt_text_edit.toPlainText()
        prompt_text = self.prompt_text_edit.prompt_text_edit.toPlainText()

        selected_card_type = self.profile_creation_settings.card_types_combo_box.currentText()
        selected_model = self.profile_creation_settings.ai_models_combo_box.currentText()
        selected_fields_dict:dict[str, bool] = self.profile_creation_settings.fields_selection_check_boxes.fields_status

        selected_fields = [field for field, checked in selected_fields_dict.items() if checked]

        fields_setting_tab = self.profile_creation_settings.settings_tabs.fields_setting_tab
        fields_setting_data: dict[str, dict[str, bool]] = fields_setting_tab.fields_settings._field_data

        general_setting_tab = self.profile_creation_settings.settings_tabs.general_settings_tab
        generate_data_as_new_cards = general_setting_tab.generate_as_new_cards_checkbox.isChecked()

        selected_deck_for_new_generated_cards = (
            general_setting_tab.choose_deck_combo_box.currentText()
            if generate_data_as_new_cards else None
        )

        tag_for_new_generated_cards = (
            general_setting_tab.add_tag_to_generated_cards_checkbox.isChecked()
            if generate_data_as_new_cards else None
        )

        tag_name_for_new_generated_cards = (
            general_setting_tab.tag_name_line_edit.text()
            if tag_for_new_generated_cards else None
        )

        profile_name = general_setting_tab.enter_profile_name_line_edit.text()

        aqt.utils.showInfo(f"{prompt_text}"
                           f"\n"
                           f"{selected_card_type}"
                           f"\n"
                           f"{selected_fields}"
                           f"\n"
                           f"{selected_model}"
                           f"\n"
                           f"{fields_setting_data}"
                           f"\n"
                           f"Generate data as new cards: {generate_data_as_new_cards}"
                           f"\n"
                           f"{selected_deck_for_new_generated_cards}"
                           f"\n"
                           f"Generate data with the tag: {tag_for_new_generated_cards}"
                           f"\n"
                           f"{tag_name_for_new_generated_cards}"
                           f"\n"
                           f"{profile_name}"
                           f"\n"
                           )


class PromptTextEditLayout(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        grid = aqt.qt.QGridLayout(self)

        self.prompt_label = aqt.qt.QLabel("Prompt")
        self.prompt_label.setSizePolicy(aqt.qt.QSizePolicy.Policy.Fixed, aqt.qt.QSizePolicy.Policy.Fixed)

        self.prompt_text_edit = aqt.qt.QPlainTextEdit()
        self.prompt_text_edit.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Expanding)
        self.prompt_text_edit.setPlaceholderText("Enter your prompt here")
        self.prompt_text_edit.setToolTip("")  # TODO: Write a proper tool tip for prompt text edit

        grid.addWidget(self.prompt_label, 0, 0)
        grid.addWidget(self.prompt_text_edit, 1, 0)

        grid.setRowStretch(1, 1)


class ProfileCreationSettings(aqt.qt.QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.card_types_combo_box = CardTypesComboBox()
        self.fields_selection_check_boxes = FieldsSelectionCheckBoxes()
        self.ai_models_combo_box = AiModelsComboBox()
        self.ai_model_prices = AiModelPricesLayout()

        self.settings_tabs = SettingTabs()
        self.create_profile_button = aqt.qt.QPushButton("Create Profile")
        self.create_profile_button.setStyleSheet("margin-bottom: 9px") # ALign the create_profile_button with prompt text edit

        self._reset_fields_settings_on_card_type_switch() # Reset needs to be before card type fields selection update, so the data is being cleared and then we receive the seleceted fields data
        self._update_fields_selection_check_boxes_on_card_type_switch()
        self._update_ai_model_prices_on_ai_model_switch()

        self._update_expected_io_text_edits_on_selected_fields_toggle()
        self._update_fields_setting_combo_box_on_selected_fields_toggle()
        self._update_fields_settings_on_selected_fields_toggle()

        self._send_initial_signals()

        self.addWidget(self.card_types_combo_box, 0, 0)
        self.addWidget(self.fields_selection_check_boxes, 0, 1, 3, 1)
        self.addWidget(self.ai_models_combo_box, 1, 0)
        self.addLayout(self.ai_model_prices, 2, 0)
        self.addWidget(self.settings_tabs, 3, 0, 1, 2)
        self.addWidget(self.create_profile_button, 4, 0, 1, 2)

    def _send_initial_signals(self):
        self.card_types_combo_box.on_card_type_switch()
        self.ai_models_combo_box.on_ai_model_switch()
        self.fields_selection_check_boxes.on_check_box_toggled()


    def _update_fields_selection_check_boxes_on_card_type_switch(self):
        self.card_types_combo_box.card_type_switch_signal.connect(
            self.fields_selection_check_boxes.create_field_check_boxes
        )

    def _reset_fields_settings_on_card_type_switch(self):
        self.card_types_combo_box.card_type_switch_signal.connect(
            self.settings_tabs.fields_setting_tab.fields_settings.clear_field_data
        )

    def _update_ai_model_prices_on_ai_model_switch(self):
        self.ai_models_combo_box.ai_model_switch_signal.connect(
            self.ai_model_prices.set_input_price
        )

        self.ai_models_combo_box.ai_model_switch_signal.connect(
            self.ai_model_prices.set_output_price
        )

    def _update_expected_io_text_edits_on_selected_fields_toggle(self):
        self.fields_selection_check_boxes.selected_fields_toggle_signal.connect(
            self.settings_tabs.expected_input_and_output.update_text_edits
        )

    def _update_fields_setting_combo_box_on_selected_fields_toggle(self):
        self.fields_selection_check_boxes.selected_fields_toggle_signal.connect(
            self.settings_tabs.fields_setting_tab.fields_setting_combo_box.set_fields_to_combo_box
        )

    def _update_fields_settings_on_selected_fields_toggle(self):
        self.fields_selection_check_boxes.selected_fields_toggle_signal.connect(
            self.settings_tabs.fields_setting_tab.fields_settings.sync_with_selected_fields
        )


class CardTypesComboBox(aqt.qt.QComboBox):
    card_type_switch_signal = aqt.qt.pyqtSignal(list)

    def __init__(self, parent: aqt.qt.QWidget | None=None):
        super().__init__(parent)

        self.currentIndexChanged.connect(self.on_card_type_switch)
        self.addItems(mw.col.models.all_names())

    def on_card_type_switch(self):
        card_type_str = str(self.currentText())

        card_type_id = mw.col.models.by_name(card_type_str)
        card_type_fields_list = mw.col.models.field_names(card_type_id)

        self.card_type_switch_signal.emit(card_type_fields_list)


class FieldsSelectionCheckBoxes(aqt.qt.QWidget):
    selected_fields_toggle_signal = aqt.qt.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        grid = aqt.qt.QGridLayout(self)

        self.scrollable_fields_check_boxes_widget = aqt.qt.QWidget()
        self.fields_check_boxes_vertical_layout = aqt.qt.QVBoxLayout(self.scrollable_fields_check_boxes_widget)
        self.check_boxes_list = []
        self.fields_status = {}

        self.scroll_area = aqt.qt.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scrollable_fields_check_boxes_widget)

        self.scroll_area.setFixedHeight(180)

        grid.addWidget(self.scroll_area, 0, 0)

    def create_field_check_boxes(self, fields_list):
        self.clear_field_check_boxes()

        for field in fields_list:
            check_box = aqt.qt.QCheckBox(str(field))
            check_box.toggled.connect(self.on_check_box_toggled)

            self.fields_check_boxes_vertical_layout.addWidget(check_box)
            self.check_boxes_list.append(check_box)

            check_box.setChecked(True)

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
        self.selected_fields_toggle_signal.emit(self.fields_status)


class AiModelsComboBox(aqt.qt.QComboBox):
    ai_model_switch_signal = aqt.qt.pyqtSignal(str)

    def __init__(self, parent: aqt.qt.QWidget | None=None):
        super().__init__(parent)

        self.addItems(AVAILABLE_MODELS)
        self.currentIndexChanged.connect(self.on_ai_model_switch)

    def on_ai_model_switch(self):
        model_name = str(self.currentText())
        self.ai_model_switch_signal.emit(model_name)


class AiModelPricesLayout(aqt.qt.QGridLayout):
    def __init__(self, parent: aqt.qt.QWidget | None=None):
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

    def set_input_price(self, model_name: str):
        input_price = MODELS_INPUT_PRICES[model_name]
        self.input_price_line.setText(decide_price_format(input_price) + "$")

    def set_output_price(self, model_name: str):
        output_price = MODELS_OUTPUT_PRICES[model_name]
        self.output_price_line.setText(decide_price_format(output_price) + "$")


class SettingTabs(aqt.qt.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setting_widget = aqt.qt.QWidget()
        self.setting_layout = aqt.qt.QVBoxLayout(self.setting_widget)

        self.expected_input_and_output = ExpectedInputAndOutput()
        self.fields_setting_tab = FieldsSettingsTab()
        self.general_settings_tab = GeneralSettingsTab()

        self.addTab(self.fields_setting_tab, "Fields settings")
        self.addTab(self.expected_input_and_output, "Expected Input and Output")
        self.addTab(self.general_settings_tab, "General settings")


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


class FieldsSettingsTab(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        grid = aqt.qt.QGridLayout(self)

        self.fields_setting_combo_box = FieldsSettingsComboBox()
        self.fields_settings = FieldsSettings()
        self.fields_settings_table = FieldsSettingsTable()

        self.fields_setting_combo_box.currentTextChanged.connect(
            self._load_setting_for_selected_field_in_combo_box
        )

        self.fields_settings.fields_settings_changed.connect(
            self.fields_settings_table.load_fields_setting_data
        )

        self.fields_setting_combo_box.setStyleSheet("margin: 15px;")

        grid.addWidget(self.fields_setting_combo_box, 0, 0, 1, 1, aqt.qt.Qt.AlignmentFlag.AlignTop | aqt.qt.Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.fields_settings, 0, 1, 1, 1, aqt.qt.Qt.AlignmentFlag.AlignTop | aqt.qt.Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.fields_settings_table, 1, 0, 1, 2)

        self.fields_setting_combo_box.setFixedWidth(200)

    def _load_setting_for_selected_field_in_combo_box(self, new_selected_field: str):
        if new_selected_field:
            self.fields_settings.load_field_settings(new_selected_field)


class FieldsSettingsComboBox(aqt.qt.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_fields_to_combo_box(self, fields_status: dict[str, bool]) -> None:
        previous_selection = self.currentText()
        self.clear()

        selected_fields = [field for field, value in fields_status.items() if value]
        self.addItems(selected_fields)

        if previous_selection in selected_fields:
            self.setCurrentText(previous_selection)


class FieldsSettings(aqt.qt.QWidget):
    fields_settings_changed = aqt.qt.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        v_layout = aqt.qt.QVBoxLayout(self)

        self._field_data: dict[str, dict[str, bool]] = {}
        self._current_field = ""

        self.fields_setting_label = aqt.qt.QLabel("All Fields Settings:")
        self.strip_html_check_box = aqt.qt.QCheckBox("Strip HTML in fields")
        self.strip_brackets_check_box = aqt.qt.QCheckBox("Strip brackets in fields")
        self.strip_non_ascii_check_box = aqt.qt.QCheckBox("Strip non-ascii characters in fields")

        self.strip_html_check_box.toggled.connect(self._update_fields_data)
        self.strip_brackets_check_box.toggled.connect(self._update_fields_data)
        self.strip_non_ascii_check_box.toggled.connect(self._update_fields_data)

        v_layout.addWidget(self.fields_setting_label)
        v_layout.addWidget(self.strip_html_check_box)
        v_layout.addWidget(self.strip_brackets_check_box)
        v_layout.addWidget(self.strip_non_ascii_check_box)

        v_layout.setSpacing(12)

    def _update_fields_data(self):
        if not self._current_field:
            return

        self._field_data[self._current_field] = {
            "strip_html" : self.strip_html_check_box.isChecked(),
            "strip_brackets" : self.strip_brackets_check_box.isChecked(),
            "strip_non_ascii" : self.strip_non_ascii_check_box.isChecked()
        }

        self.fields_settings_changed.emit(self._field_data)

    def sync_with_selected_fields(self, fields_status: dict[str, bool]):
        new_fields_data = {}  # New dict is created, so items are sorted in the same way as in fields_status

        for field, checked in fields_status.items():
            if not checked:
                continue

            if field in self._field_data:
                new_fields_data[field] = self._field_data[field]
            else:
                new_fields_data[field] = {
                    "strip_html": False,
                    "strip_brackets": False,
                    "strip_non_ascii": False
                }

        self._field_data = new_fields_data
        self.fields_settings_changed.emit(self._field_data)

    def clear_field_data(self):
        self._field_data.clear()

        self._block_signals_to_check_boxes(True)

        self.strip_html_check_box.setChecked(False)
        self.strip_brackets_check_box.setChecked(False)
        self.strip_non_ascii_check_box.setChecked(False)

        self._block_signals_to_check_boxes(False)

        self.fields_settings_changed.emit(self._field_data)

    def _block_signals_to_check_boxes(self, state: bool):
        self.strip_html_check_box.blockSignals(state)
        self.strip_brackets_check_box.blockSignals(state)
        self.strip_non_ascii_check_box.blockSignals(state)

    def load_field_settings(self, new_selected_field: str):
        if new_selected_field in self._field_data.keys():
            self._current_field = new_selected_field
            self.fields_setting_label.setText(f"{self._current_field} Field Settings:")

            settings = self._field_data[self._current_field]

            self._block_signals_to_check_boxes(True)

            self.strip_html_check_box.setChecked(settings["strip_html"])
            self.strip_brackets_check_box.setChecked(settings["strip_brackets"])
            self.strip_non_ascii_check_box.setChecked(settings["strip_non_ascii"])

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

    def load_fields_setting_data(self, fields_setting_data: dict[str, dict[str, bool]]):
        selected_fields = [field for field in fields_setting_data.keys()]
        selected_fields_length = len(selected_fields)
        self.setRowCount(selected_fields_length)

        for row_index in range(selected_fields_length):
            field_name = selected_fields[row_index]
            self.setItem(row_index, 0, aqt.qt.QTableWidgetItem(field_name))

            field_settings = fields_setting_data[field_name]

            for col_index, strip_setting in enumerate(("strip_html", "strip_brackets", "strip_non_ascii"), start=1):
                self.setItem(
                    row_index,
                    col_index,
                    create_table_check_item(checked=field_settings[strip_setting])
                )


class GeneralSettingsTab(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = aqt.qt.QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(50)

        left_layout = aqt.qt.QVBoxLayout()
        left_layout.setSpacing(0)

        self.generate_as_new_cards_checkbox = aqt.qt.QCheckBox("Generate data as a new cards")

        self.choose_deck_label = aqt.qt.QLabel("Choose deck to save generated cards in:")
        self.choose_deck_combo_box = aqt.qt.QComboBox()
        self.choose_deck_combo_box.setFixedWidth(220)

        self.add_tag_to_generated_cards_checkbox = aqt.qt.QCheckBox("Add tag to generated cards")
        self.enter_tag_name_label = aqt.qt.QLabel("Enter tag name:")
        self.tag_name_line_edit = aqt.qt.QLineEdit()
        self.tag_name_line_edit.setFixedWidth(220)

        left_layout.addWidget(self.generate_as_new_cards_checkbox)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.choose_deck_label)
        left_layout.addSpacing(6)
        left_layout.addWidget(self.choose_deck_combo_box)
        left_layout.addSpacing(18)
        left_layout.addWidget(self.add_tag_to_generated_cards_checkbox)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.enter_tag_name_label)
        left_layout.addSpacing(6)
        left_layout.addWidget(self.tag_name_line_edit)
        left_layout.addStretch(1)

        # --- Right Column (Profile Settings) ---
        right_layout = aqt.qt.QVBoxLayout()
        right_layout.setSpacing(8)

        self.enter_profile_name_label = aqt.qt.QLabel("Enter profile name:")
        self.enter_profile_name_line_edit = aqt.qt.QLineEdit()
        self.enter_profile_name_line_edit.setFixedWidth(220)

        right_layout.addWidget(self.enter_profile_name_label)
        right_layout.addWidget(self.enter_profile_name_line_edit)
        right_layout.addStretch(1)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.addStretch(1)

        self._add_deck_names_to_the_combo_box()
        self._create_opacity_effects()

        self.generate_as_new_cards_checkbox.toggled.connect(self._switch_other_widgets_opacity)
        self.add_tag_to_generated_cards_checkbox.toggled.connect(self._switch_add_tag_widget_opacity)

        self._switch_other_widgets_opacity(self.generate_as_new_cards_checkbox.isChecked())
        self._switch_add_tag_widget_opacity(self.add_tag_to_generated_cards_checkbox.isChecked())

    def _create_opacity_effects(self):
        self.widgets_with_opacity_effect = [
            self.choose_deck_label,
            self.choose_deck_combo_box,
            self.add_tag_to_generated_cards_checkbox,
            self.enter_tag_name_label,
            self.tag_name_line_edit,
        ]

        self.opacity_effects_list = []
        for index, widget in enumerate(self.widgets_with_opacity_effect):
            effect = aqt.qt.QGraphicsOpacityEffect(widget)
            self.opacity_effects_list.append(effect)
            widget.setGraphicsEffect(effect)

    def _switch_other_widgets_opacity(self, checked: bool):
        widget_and_opacity_effect_tuple = zip(
            self.widgets_with_opacity_effect[0:3], self.opacity_effects_list[0:3]
        )
        opacity = 1.0 if checked else 0.5

        for widget, opacity_effect in widget_and_opacity_effect_tuple:
            widget.setEnabled(checked)
            opacity_effect.setOpacity(opacity)

            if not checked and isinstance(widget, aqt.qt.QCheckBox):
                widget.setChecked(False)

    def _switch_add_tag_widget_opacity(self, checked: bool):
        widget_and_opacity_effect_tuple = zip(
            self.widgets_with_opacity_effect[3:], self.opacity_effects_list[3:]
        )
        opacity = 1.0 if checked else 0.5

        for widget, opacity_effect in widget_and_opacity_effect_tuple:
            widget.setEnabled(checked)
            opacity_effect.setOpacity(opacity)

            if not checked and isinstance(widget, aqt.qt.QLineEdit):
                widget.clear()

    def _add_deck_names_to_the_combo_box(self):
        deck_names: list[str] = mw.col.decks.all_names()
        self.choose_deck_combo_box.addItems(deck_names)


def decide_price_format(price: float) -> str:
    three_digits_after_decimal_point_price = f"{price:.3f}"
    if three_digits_after_decimal_point_price.endswith("0"):
        return f"{price:.2f}"

    return three_digits_after_decimal_point_price

def create_table_check_item(checked: bool) -> aqt.qt.QTableWidgetItem:
    green = "#4CAF50"
    red = "#F44336"

    symbol = "✔" if checked else "✖"
    color = green if checked else red

    item = aqt.qt.QTableWidgetItem(symbol)
    item.setForeground(aqt.qt.QColor(color))
    item.setTextAlignment(aqt.Qt.AlignmentFlag.AlignCenter)
    return item

def open_configuration_dialog(browser: Browser) -> None:
    configuration_dialog = ProfileConfigurationDialog(browser)
    configuration_dialog.exec()
