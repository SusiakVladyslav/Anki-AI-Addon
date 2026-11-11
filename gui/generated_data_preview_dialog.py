import aqt

from ..ai.openai_requests import AiOutput
from ..gui import ui_constants

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
        self.original_data: list[dict[str, str]] = self._get_data_from_selected_notes()
        self.column_names = []

        grid = aqt.QGridLayout(self)

        self.table = aqt.qt.QTableWidget()

        self.table.setRowCount(self._calculate_amount_of_rows())
        self.table.setColumnCount(self._calculate_amount_of_cols())

        self._set_column_names()
        self._populate_table()
        self._configure_table_view()

        self.commit_buttons_box = aqt.qt.QDialogButtonBox(
            aqt.qt.QDialogButtonBox.StandardButton.Ok
            | aqt.qt.QDialogButtonBox.StandardButton.Cancel
        )

        ok_button = self.commit_buttons_box.button(aqt.qt.QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setText("Confirm")

        self.commit_buttons_box.rejected.connect(self.reject)
        self.commit_buttons_box.accepted.connect(self.accept)

        grid.addWidget(self.table, 0, 0, 1, 2)
        grid.addWidget(self.commit_buttons_box, 1, 1, 1, 1)

    def _get_data_from_selected_notes(self) -> list[dict[str, str]]:
        notes_data = []

        for note in self.selected_notes:
            note_dict = {}
            for field_name, field_data in note.items():
                if field_name in self.selected_fields:
                    note_dict[field_name] = field_data
            notes_data.append(note_dict)

        return notes_data

    def _calculate_amount_of_rows(self) -> int:
        """Each row represents one note that is being enhanced."""
        return len(self.selected_notes)

    def _calculate_amount_of_cols(self) -> int:
        """
        Each field in selected fields represents two columns:
            First column is the original data from the field
            Second column is the AI-generated data for the field.
        """
        return len(self.selected_fields) * 2

    def _set_column_names(self) -> None:
        for field_name in self.selected_fields:
            self.column_names.extend([f"Original {field_name}", f"Generated {field_name}"])

        self.table.setHorizontalHeaderLabels(self.column_names)

    def _populate_table(self) -> None:
        for row_idx, (original_note, generated_note) in enumerate(zip(self.original_data, self.generated_notes)):
            col_idx = 0

            for field_name in original_note.keys():
                original_value = original_note[field_name]
                generated_value = generated_note[field_name]

                self._set_label_cell(row_idx, col_idx, original_value)
                col_idx += 1

                self._set_label_cell(row_idx, col_idx, generated_value)
                col_idx += 1

    def _set_label_cell(self, row: int, col: int, text: str) -> None:
        label = aqt.qt.QLabel(str(text))
        label.setWordWrap(True)

        self.table.setCellWidget(row, col, label)

    def _configure_table_view(self) -> None:
        self.table.setVerticalScrollMode(aqt.qt.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setHorizontalScrollMode(aqt.qt.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.verticalScrollBar().setSingleStep(20)

        self.table.setShowGrid(True)
        self.table.setGridStyle(aqt.qt.Qt.PenStyle.SolidLine)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {ui_constants.GRAY_GRIDLINE_COLOR};
                font-size: {ui_constants.QTABLEWIDGET_FONT_SIZE}pt;
            }}
            QTableWidget::item {{
                padding: {ui_constants.TABLE_ITEM_PADDING}px;
                font-size: {ui_constants.QTABLEWIDGET_FONT_SIZE}pt;
            }}
            QTableWidget QLabel {{
                font-size: {ui_constants.QTABLEWIDGET_FONT_SIZE}pt;
            }}
            QHeaderView::section {{
                font-size: {ui_constants.QTABLEWIDGET_HEADER_FONT_SIZE}pt;
            }}
        """)

        self.header = self.table.horizontalHeader()
        self.v_header = self.table.verticalHeader()

        self.header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)
        self.header.setDefaultSectionSize(ui_constants.TABLE_COLUMN_WIDTH)

        for row in range(self.table.rowCount()):
            required_height_for_row = self._calculate_row_height(row)
            self.table.setRowHeight(
                row, min(required_height_for_row, ui_constants.TABLE_MAX_ROW_HEIGHT)
            )

        self.v_header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)

    def _calculate_row_height(self, row: int) -> int:
        required_height_for_row = 0

        for col in range(self.table.columnCount()):
            label = self.table.cellWidget(row, col)

            if label is None:
                continue

            column_width = self.table.columnWidth(col)

            required_height_for_cell = label.heightForWidth(column_width)

            required_height_for_row = max(
                required_height_for_row,
                required_height_for_cell
            )

        # There is padding of other widgets that are hard to control, so to account for that extra space is added
        extra_safety_space = ui_constants.EXTRA_SAFETY_SPACE_PADDING
        return required_height_for_row + ui_constants.TABLE_ITEM_PADDING * 2 + extra_safety_space