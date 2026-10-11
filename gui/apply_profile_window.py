import aqt.qt
from aqt.browser import Browser
from aqt import mw

from . import gui_utils
from .create_profile_configuration import ProfileConfigurationDialog

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
        self.profile_settings = gui_utils.get_profile_settings_from_config(self.profile_name)

        self.profile_edit_buttons = ProfileEditButtons(self.profile_name)
        self.notes_data_table = NotesDataTable(self, self.selected_notes, self.profile_settings)
        self.commit_buttons = CommitButtons()

        self.profile_edit_buttons.edit_requested.connect(self._show_edit_configuration)

        self.commit_buttons.commit_buttons_box.rejected.connect(self.reject)
        self.commit_buttons.commit_buttons_box.accepted.connect(self.accept)

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(self.profile_edit_buttons, 0, 0)
        grid.addWidget(self.notes_data_table, 1, 0)
        grid.addWidget(self.commit_buttons, 2, 0)

    def _show_edit_configuration(self):
        edit_configuration_dialog = ProfileConfigurationDialog(self.parent)
        edit_configuration_dialog.load_profile_settings(self.profile_name, self.profile_settings)
        edit_configuration_dialog.open()



class ProfileEditButtons(aqt.qt.QWidget):
    show_settings_requested = aqt.qt.pyqtSignal()
    edit_requested = aqt.qt.pyqtSignal()
    delete_requested = aqt.qt.pyqtSignal()
    duplicate_requested = aqt.qt.pyqtSignal()

    def __init__(self, profile_name:str, parent=None):
        super().__init__(parent)

        self.profile_name_label = aqt.qt.QLabel(f"Profile:{profile_name}")
        self.show_settings_button = aqt.qt.QPushButton("Show Settings")
        self.edit_button = aqt.qt.QPushButton("Edit")
        self.delete_button = aqt.qt.QPushButton("Delete")
        self.duplicate_button = aqt.qt.QPushButton("Duplicate")

        self.show_settings_button.clicked.connect(self.show_settings_requested)
        self.edit_button.clicked.connect(self.edit_requested)
        self.delete_button.clicked.connect(self.delete_requested)
        self.duplicate_button.clicked.connect(self.duplicate_requested)

        h_layout = aqt.qt.QHBoxLayout(self)

        h_layout.addWidget(self.profile_name_label)
        h_layout.addWidget(self.show_settings_button)
        h_layout.addWidget(self.edit_button)
        h_layout.addWidget(self.delete_button)
        h_layout.addWidget(self.duplicate_button)


class NotesDataTable(aqt.qt.QWidget):
    def __init__(self, parent=None, selected_notes=None, profile_settings=None):
        super().__init__(parent)

        self.profile_settings = profile_settings
        self.selected_notes = selected_notes

        self.selected_fields:list[str] = self.profile_settings["selected_fields"]

        self.table = aqt.qt.QTableWidget()

        self.table.setColumnCount(self._calculate_amount_of_cols())
        self.table.setRowCount(self._calculate_amount_of_rows())
        self._set_columns_names()
        self._populate_table()

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(self.table, 0, 0)

    def _calculate_amount_of_cols(self):
        note_id_and_card_type_columns = 2
        original_field_data_and_processed_field_data_columns_per_selected_field = 2 * len(self.selected_fields)

        return note_id_and_card_type_columns + original_field_data_and_processed_field_data_columns_per_selected_field
        return 2 + 2 * len(self.selected_fields)

    def _calculate_amount_of_rows(self):
        return len(self.selected_notes)

    def _set_columns_names(self):
        columns_names = ["Note ID", "Card Type"]
        for field_name in self.selected_fields:
            columns_names.extend([f"Original {field_name}", f"Processed {field_name}"])

        self.table.setHorizontalHeaderLabels(columns_names)

    def _populate_table(self):
        for row in range(self.table.rowCount()):
            note = self.selected_notes[row]
            note_id_item = aqt.qt.QTableWidgetItem(str(note.id))
            note_card_type_item = aqt.qt.QTableWidgetItem(mw.col.models.get(note.mid)["name"])

            self.table.setItem(row, 0, note_id_item)
            self.table.setItem(row, 1, note_card_type_item)

            col = 2
            for field_name, field_data in note.items():

                if field_name in self.selected_fields:
                    original_data_item = aqt.qt.QTableWidgetItem(str(field_data))
                    processed_data_item = aqt.qt.QTableWidgetItem(str(field_data))

                    self.table.setItem(row, col, original_data_item)
                    self.table.setItem(row, col + 1, processed_data_item)
                    col += 2


class CommitButtons(aqt.qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        commit_buttons = (
            aqt.qt.QDialogButtonBox.StandardButton.Apply
            | aqt.qt.QDialogButtonBox.StandardButton.Cancel
        )

        self.commit_buttons_box = aqt.qt.QDialogButtonBox(commit_buttons)

        h_layout = aqt.qt.QHBoxLayout(self)
        h_layout.addWidget(self.commit_buttons_box)

