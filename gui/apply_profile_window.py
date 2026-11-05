import aqt.theme
import aqt.qt
from aqt.browser import Browser
from aqt import mw

from typing import Any

from . import gui_utils
from .create_profile_configuration import ProfileConfigurationDialog, DialogMode
from ..utils.profile_service import ProfileService
from . import style
from . import dialogs


class ApplyProfileDialog(aqt.qt.QDialog):
    def __init__(self, parent:Browser, profile_name:str):
        super().__init__(parent)

        self.setWindowTitle("Apply Profile")
        self.resize(1200, 800)
        self.setModal(False)
        self.setSizeGripEnabled(True)

        self.parent = parent

        self.profile_name = profile_name
        self.selected_notes = gui_utils.get_selected_notes(self.parent)
        self.profile_settings: dict[str, Any] = gui_utils.get_profile_settings_from_config(self.profile_name)

        self.profile_edit_buttons = ProfileEditButtons(self.profile_name)
        self.notes_data_table = NotesDataTable(self, self.selected_notes, self.profile_settings)
        self.commit_buttons = CommitButtons()

        self.profile_edit_buttons.edit_requested.connect(self._open_edit_configuration)
        self.profile_edit_buttons.delete_requested.connect(self.delete_profile)
        self.profile_edit_buttons.duplicate_requested.connect(self.duplicate_profile)

        self.commit_buttons.commit_buttons_box.rejected.connect(self.reject)
        self.commit_buttons.apply_button.clicked.connect(self.apply_to_notes)

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(self.profile_edit_buttons, 0, 0)
        grid.addWidget(self.notes_data_table, 1, 0)
        grid.addWidget(self.commit_buttons, 2, 0)

    def apply_to_notes(self):
        input_data = self.notes_data_table.extract_processed_data_from_table()

        selected_notes_with_correct_card_type = []
        for note in self.selected_notes:
            note_card_type = mw.col.models.get(note.mid)["name"]
            if note_card_type == self.profile_settings["selected_card_type"]:
                selected_notes_with_correct_card_type.append(note)

        profile_service = ProfileService(browser=self.parent, profile_settings=self.profile_settings)
        profile_service.apply_profile(parent=self, input_data=input_data, selected_notes=selected_notes_with_correct_card_type)
        self.accept()

    def _open_edit_configuration(self):
        self.edit_configuration_dialog = ProfileConfigurationDialog(
            mode=DialogMode.Edit(profile_name=self.profile_name, profile_settings=self.profile_settings),
            parent=self.parent
        )
        self.edit_configuration_dialog.profile_settings_changed.connect(self.load_edited_settings)
        self.edit_configuration_dialog.open()

    def delete_profile(self):
        deletion_confirmed: bool = aqt.utils.askUser(
            f'Are you sure you want to delete profile "{self.profile_name}"?',
            parent=self.parent,
            title="Confirm Deletion"
        )

        if deletion_confirmed:
            gui_utils.delete_profile_from_config(self.profile_name)
            aqt.utils.showInfo(f"Profile {self.profile_name} was successfully deleted")
            self.accept()

    def duplicate_profile(self):
        dialog = DuplicateProfileDialog(self.profile_name, self)
        dialog.show()


    def load_edited_settings(self, new_profile_settings):
        self.profile_name = next(iter(new_profile_settings))
        self.profile_settings = new_profile_settings[self.profile_name]

        self.profile_edit_buttons.profile_name_label.setText(f"Profile: {self.profile_name}")

        self.notes_data_table.profile_settings = self.profile_settings
        self.notes_data_table.selected_fields = self.profile_settings["selected_fields"]
        self.notes_data_table.selected_fields_settings = self.profile_settings["selected_fields_settings"]
        self.notes_data_table.clear_table()

        self.notes_data_table.table.setColumnCount(self.notes_data_table._calculate_amount_of_cols())
        self.notes_data_table.table.setRowCount(self.notes_data_table._calculate_amount_of_rows())
        self.notes_data_table._set_columns_names()
        self.notes_data_table._populate_table()
        self.notes_data_table._configure_table_view()


class DuplicateProfileDialog(aqt.qt.QDialog):
    def __init__(self, profile_name: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Duplicate Profile")
        self.resize(375, 100)

        self.original_profile_name = profile_name

        v_layout = aqt.qt.QVBoxLayout(self)

        v_layout.addStretch(1)

        self.label = aqt.qt.QLabel(
            f"Enter a name for the duplicated profile (max {style.PROFILE_NAME_MAX_LENGTH} characters):"
        )
        v_layout.addWidget(self.label)

        self.line_edit = aqt.qt.QLineEdit()
        self.line_edit.setText(f"{profile_name} (Duplicate)")
        v_layout.addWidget(self.line_edit)

        v_layout.addStretch(1)

        self.button_box = aqt.qt.QDialogButtonBox(
            aqt.qt.QDialogButtonBox.StandardButton.Ok | aqt.qt.QDialogButtonBox.StandardButton.Cancel
        )
        v_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def accept(self):
        duplicate_profile_name = self.line_edit.text()

        if duplicate_profile_name == "":
            dialogs.profile_name_cant_be_empty_warning(parent=self)
            return

        if len(duplicate_profile_name) > style.PROFILE_NAME_MAX_LENGTH:
            dialogs.profile_name_is_too_long_warning(duplicate_profile_name, parent=self)
            return

        original_profile_settings = gui_utils.get_profile_settings_from_config(self.original_profile_name)
        duplicate_settings = {duplicate_profile_name: original_profile_settings}

        if gui_utils.insert_profile_settings_in_config(duplicate_settings):
            super().accept()
            dialogs.profile_was_successfully_created(duplicate_profile_name, parent=self)

class ProfileEditButtons(aqt.qt.QWidget):
    edit_requested = aqt.qt.pyqtSignal()
    delete_requested = aqt.qt.pyqtSignal()
    duplicate_requested = aqt.qt.pyqtSignal()

    def __init__(self, profile_name:str, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QLabel {{
                font-size: {style.APPLY_PROFILE_LABEL_FONT_SIZE}pt;
            }}
            QPushButton {{
                font-size: {style.APPLY_PROFILE_BUTTONS_FONT_SIZE}pt;
            }}
        """)

        self.profile_name_label = aqt.qt.QLabel(f'Profile: "{profile_name}"')

        self.edit_button = aqt.qt.QPushButton("Edit")
        self.delete_button = aqt.qt.QPushButton("Delete")
        self.duplicate_button = aqt.qt.QPushButton("Duplicate")

        self.edit_button.clicked.connect(self.edit_requested)
        self.delete_button.clicked.connect(self.delete_requested)
        self.duplicate_button.clicked.connect(self.duplicate_requested)

        h_layout = aqt.qt.QHBoxLayout(self)

        h_layout.addWidget(self.profile_name_label)
        h_layout.addWidget(self.edit_button)
        h_layout.addWidget(self.delete_button)
        h_layout.addWidget(self.duplicate_button)


class NotesDataTable(aqt.qt.QWidget):
    def __init__(self, parent=None, selected_notes=None, profile_settings=None):
        super().__init__(parent)

        self.profile_settings = profile_settings
        self.selected_notes = selected_notes

        self.selected_fields:list[str] = self.profile_settings["selected_fields"]
        self.selected_fields_settings = self.profile_settings["selected_fields_settings"]

        self.table = aqt.qt.QTableWidget()

        self.table.setColumnCount(self._calculate_amount_of_cols())
        self.table.setRowCount(self._calculate_amount_of_rows())

        self._set_columns_names()
        self._populate_table()
        self._configure_table_view()

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(self.table, 0, 0)

    def _configure_table_view(self):
        self.table.setVerticalScrollMode(aqt.qt.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setHorizontalScrollMode(aqt.qt.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.verticalScrollBar().setSingleStep(20)

        self.table.setShowGrid(True)
        self.table.setGridStyle(aqt.qt.Qt.PenStyle.SolidLine)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color:  {style.GRAY_GRIDLINE_COLOR};
                font-size: {style.QTABLEWIDGET_FONT_SIZE}pt;
            }}
            QTableWidget::item {{
                padding: {style.TABLE_ITEM_PADDING}px;
                font-size: {style.QTABLEWIDGET_FONT_SIZE}pt;
            }}
            QHeaderView::section {{
                font-size: {style.QTABLEWIDGET_HEADER_FONT_SIZE}pt;
            }}
        """)

        self.header = self.table.horizontalHeader()
        self.v_header = self.table.verticalHeader()

        self.table.setWordWrap(True)

        self.header.setSectionResizeMode(0, aqt.qt.QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(1, aqt.qt.QHeaderView.ResizeMode.ResizeToContents)

        for col in range(2, self.table.columnCount()):
            self.table.setColumnWidth(col, style.TABLE_COLUMN_WIDTH)

        for row in range(self.table.rowCount()):
            font = self.table.font()
            font.setPointSize(style.QTABLEWIDGET_FONT_SIZE)
            font_metrics = aqt.qt.QFontMetrics(font)

            required_height_for_row = self.calculate_row_height(row, font_metrics)
            self.table.setRowHeight(
                row, min(required_height_for_row, style.TABLE_MAX_ROW_HEIGHT)
            )

        self.header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)
        self.v_header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)

    def calculate_row_height(self, row, font_metrics):
        required_height_for_row = 0

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item is None:
                continue
            cell_text = item.text()

            # There is padding of other widgets that are hard to control, so to account for that extra space is added
            extra_safety_space = style.EXTRA_SAFETY_SPACE_PADDING

            usable_width = self.table.columnWidth(col) - (style.TABLE_ITEM_PADDING * 2) - extra_safety_space
            bounding_rect = font_metrics.boundingRect(
                0, 0, usable_width, 10000, aqt.qt.Qt.TextFlag.TextWordWrap, cell_text
            )

            required_height_for_cell = bounding_rect.height() + (style.TABLE_ITEM_PADDING * 2) + extra_safety_space

            if required_height_for_cell > required_height_for_row:
                required_height_for_row = required_height_for_cell

        return required_height_for_row

    def _calculate_amount_of_cols(self):
        """
        First two columns are dedicated for note id and card type.
        Each field in selected_fields represents two columns:
            First is the original data from the field
            Second is the processed data with the strip settings.
        """
        note_id_and_card_type_columns = 2
        original_and_processed_columns = 2 * len(self.selected_fields)

        return note_id_and_card_type_columns + original_and_processed_columns

    def _calculate_amount_of_rows(self):
        """Each row represents one note selected for enhancement."""
        return len(self.selected_notes)

    def _set_columns_names(self):
        self.columns_names = ["Note ID", "Card Type"]
        for field_name in self.selected_fields:
            self.columns_names.extend([f"Original {field_name}", f"Processed {field_name}"])

        self.table.setHorizontalHeaderLabels(self.columns_names)

    def _populate_table(self):
        for row in range(self.table.rowCount()):
            note = self.selected_notes[row]
            note_card_type = mw.col.models.get(note.mid)["name"]
            note_id_item = aqt.qt.QTableWidgetItem(str(note.id))
            note_card_type_item = aqt.qt.QTableWidgetItem(note_card_type)

            self.table.setItem(row, 0, note_id_item)
            self.table.setItem(row, 1, note_card_type_item)

            col = 2

            for field_name in self.selected_fields:
                if note_card_type == self.profile_settings["selected_card_type"]:
                    field_data = note[field_name] if field_name in note else ""
                else:
                    field_data = ""

                original_data_item = aqt.qt.QTableWidgetItem(str(field_data))

                if self.selected_fields_settings.get(field_name, {}).get("strip_html", False):
                    processed_data_item = aqt.qt.QTableWidgetItem(
                        gui_utils.strip_html(str(field_data))
                    )
                else:
                    processed_data_item = aqt.qt.QTableWidgetItem(str(field_data))

                self.table.setItem(row, col, original_data_item)
                self.table.setItem(row, col + 1, processed_data_item)
                col += 2

            if note_card_type != self.profile_settings["selected_card_type"]:
                self._highlight_row_as_invalid(row)

    def _highlight_row_as_invalid(self, row: int) -> None:
        if aqt.theme.theme_manager.night_mode:
            red_color = aqt.qt.QColor(style.WRONG_CARD_TYPE_COLOR_DARK)
        else:
            red_color = aqt.qt.QColor(style.WRONG_CARD_TYPE_COLOR_LIGHT)

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(red_color)

    def clear_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def extract_processed_data_from_table(self) -> list[dict[str, str]]:
        notes = []

        for row in range(self.table.rowCount()):
            card_type_column = self.table.item(row, 1).text()
            if card_type_column != self.profile_settings["selected_card_type"]:
                continue

            notes_data = dict()

            for col, field_name in zip(range(3, self.table.columnCount(), 2), self.selected_fields):
                cell_text = self.table.item(row, col).text()
                notes_data[field_name] = cell_text

            notes.append(notes_data)

        return notes



class CommitButtons(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.commit_buttons_box = aqt.qt.QDialogButtonBox(
            aqt.qt.QDialogButtonBox.StandardButton.Apply
            | aqt.qt.QDialogButtonBox.StandardButton.Cancel
        )

        self.apply_button = self.commit_buttons_box.button(aqt.qt.QDialogButtonBox.StandardButton.Apply)

        h_layout = aqt.qt.QHBoxLayout(self)
        h_layout.addWidget(self.commit_buttons_box)

