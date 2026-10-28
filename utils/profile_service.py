import aqt.utils
from aqt import mw
from aqt.operations import QueryOp
from anki.notes import Note
from aqt.browser import Browser

from typing import Any
import json

from ..gui import dialogs
from ..gui import gui_utils
from ..ai.openai_requests import send_open_ai_request, AiOutput


class ProfileService:
    def __init__(self, browser, profile_settings):
        self.profile_settings: dict[str, Any] = profile_settings
        self.browser: Browser = browser

        self.prompt: str = self.profile_settings["prompt_text"]
        self.ai_model: str = self.profile_settings["selected_model"]

        self.selected_fields = self.profile_settings["selected_fields"]

        self.selected_card_type = self.profile_settings["selected_card_type"]
        self.generate_as_new_cards: bool = self.profile_settings["generate_as_new_cards"]
        self.deck_for_generated_cards: str | None = self.profile_settings["deck_for_generated_cards"]
        self.add_tag_to_generated_cards: bool = self.profile_settings["add_tag_to_generated_cards"]
        self.tag_name_for_generated_cards: str | None = self.profile_settings["tag_name_for_generated_cards"]

    def apply_profile(self, parent, input_data, selected_notes):
        input_data_json = json.dumps(input_data, indent=2)

        op = QueryOp(
            parent=parent,
            op = lambda _: send_open_ai_request(input_data=input_data_json, prompt=self.prompt, model=self.ai_model, selected_fields=self.selected_fields),
            success=lambda ai_output: self.show_preview_table(ai_output=ai_output, selected_notes=selected_notes, selected_fields=self.selected_fields)
        )

        op.with_progress("AI is generating sentences...").run_in_background()

    def show_preview_table(self, ai_output: AiOutput, selected_notes, selected_fields):
        preview_table_dialog = PreviewTableDialog(parent=self.browser, ai_output=ai_output, selected_notes=selected_notes, selected_fields=selected_fields)
        preview_table_dialog.accepted.connect(lambda: self._apply_results_to_notes(ai_output=ai_output, notes=selected_notes))
        preview_table_dialog.show()

        money_spent_on_input, money_spent_on_output, total_money_spent = gui_utils.calculate_spent_money(
            input_tokens= ai_output.input_tokens,
            output_tokens= ai_output.output_tokens,
            model = self.ai_model
        )

        dialogs.successful_notes_generation(
            time_spent=ai_output.time_spent,
            input_tokens=ai_output.input_tokens,
            output_tokens=ai_output.output_tokens,
            money_spent_on_input=money_spent_on_input,
            money_spent_on_output=money_spent_on_output,
            total_money_spent=total_money_spent,
            ai_model=self.ai_model,
            parent=self.browser
        )

    def _apply_results_to_notes(self, ai_output: AiOutput, notes):
        generated_notes:list[dict[str, str]] = ai_output.output_json["generated_notes"]

        if self.generate_as_new_cards:
            self._create_new_notes(generated_notes)
            dialogs.show_successful_notes_creation(
                amount_of_notes=len(generated_notes),
                creation_deck=self.deck_for_generated_cards,
                parent=self.browser
            )
        else:
            self._replace_existing_notes(generated_notes, notes)
            dialogs.show_successful_notes_replacement(parent=self.browser)

        self.browser.onSearchActivated()
        if self.browser.editor.note:
            self.browser.editor.loadNote()

    def _create_new_notes(self, generated_notes:list[dict[str, str]]):
        deck_id = mw.col.decks.id_for_name(self.deck_for_generated_cards)
        note_type = mw.col.models.by_name(self.selected_card_type)

        for generated_note in generated_notes:
            new_note = mw.col.new_note(note_type)

            for field_name, field_data in generated_note.items():
                new_note[field_name] = field_data

                if self.add_tag_to_generated_cards:
                    new_note.add_tag(self.tag_name_for_generated_cards) # if tag_name contains space it will add a tag for each word instead of just 1 tag

            mw.col.add_note(new_note, deck_id)

    @staticmethod
    def _replace_existing_notes(generated_notes: list[dict[str, str]], selected_notes: list[Note]):
        for note, note_dict in zip(selected_notes, generated_notes):
            for field_name, field_data in note_dict.items():
                note[field_name] = field_data

            note.col.update_note(note)


class PreviewTableDialog(aqt.qt.QDialog):
    def __init__(self, selected_notes, selected_fields, ai_output: AiOutput, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Preview")
        self.resize(1200, 800)
        self.setModal(False)
        self.setSizeGripEnabled(True)

        self.selected_fields = selected_fields
        self.selected_notes = selected_notes
        self.generated_notes: list[dict[str, str]] = ai_output.output_json["generated_notes"]
        self.original_data: list[dict[str, str]] = self.get_data_from_selected_notes()
        self.column_names = []

        grid = aqt.QGridLayout(self)

        self.table = aqt.qt.QTableWidget()

        self.table.setRowCount(len(self.selected_notes))
        self.table.setColumnCount(len(self.original_data[0]) * 2)

        self.set_column_names()
        self.populate_table()
        self._configure_table_view()

        self.commit_buttons_box = aqt.qt.QDialogButtonBox(
            aqt.qt.QDialogButtonBox.StandardButton.Ok
            | aqt.qt.QDialogButtonBox.StandardButton.Cancel
        )

        self.commit_buttons_box.rejected.connect(self.reject)
        self.commit_buttons_box.accepted.connect(self.accept)

        grid.addWidget(self.table, 0, 0, 1, 2)
        grid.addWidget(self.commit_buttons_box, 1, 1, 1, 1)

    def get_data_from_selected_notes(self) -> list[dict[str, str]]:
        notes_data = []

        for note in self.selected_notes:
            note_dict = {}
            for field_name, field_data in note.items():
                if field_name in self.selected_fields:
                    note_dict[field_name] = field_data
            notes_data.append(note_dict)

        return notes_data

    def set_column_names(self):
        for field_name in self.original_data[0].keys():
            self.column_names.extend([f"Original {field_name}", f"Generated {field_name}"])

        self.table.setHorizontalHeaderLabels(self.column_names)

    def populate_table(self):
        for row_idx, (original_note, generated_note) in enumerate(zip(self.original_data, self.generated_notes)):
            col_idx = 0

            for field_name in original_note.keys():
                original_value = original_note[field_name]
                generated_value = generated_note[field_name]

                self._set_label_cell(row_idx, col_idx, original_value)
                col_idx += 1

                self._set_label_cell(row_idx, col_idx, generated_value)
                col_idx += 1

        self.table.resizeRowsToContents()

    def _set_label_cell(self, row: int, col: int, text: str) -> None:
        label = aqt.qt.QLabel(str(text))
        label.setWordWrap(True)
        label.setContentsMargins(6, 4, 6, 4)

        self.table.setCellWidget(row, col, label)

    def _configure_table_view(self):
        self.table.setVerticalScrollMode(aqt.qt.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setHorizontalScrollMode(aqt.qt.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.verticalScrollBar().setSingleStep(20)

        self.table.setShowGrid(True)
        self.table.setGridStyle(aqt.qt.Qt.PenStyle.SolidLine)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #777777;
            }
        """)

        self.header = self.table.horizontalHeader()
        self.v_header = self.table.verticalHeader()

        # Set columns to interactive resizing with default width
        self.header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)
        self.header.setDefaultSectionSize(280)

        # Allow vertical header to accept explicit row heights from resizeRowsToContents()
        self.v_header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)