import aqt.qt
from PyQt6.QtGui import QTextLine
from PyQt6.QtWidgets import QGridLayout, QPushButton, QLabel, QVBoxLayout
from aqt.browser import Browser

class ConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Configuration")
        self.resize(800, 600)
        self.setModal(False)
        self.setSizeGripEnabled(True)

        plain_text_edit = aqt.qt.QPlainTextEdit()
        plain_text_edit.setPlaceholderText("Placeholder text")

        grid = aqt.qt.QGridLayout(self)
        grid.addWidget(plain_text_edit, 0, 0)
        grid.addLayout(second_half_of_the_window(),0 ,1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)


class second_half_of_the_window(aqt.qt.QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.addLayout(NoteFieldsCheckBoxes(fields_list=["Korean", "English", "Hanja", "Number", "Front", "Back", "Audio"]), 0, 1)

        button1 = QPushButton("Click me")
        button1.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Expanding)
        button2 = QPushButton("Click me")
        button2.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Expanding)
        button3 = QPushButton("Click me")
        button3.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Expanding)
        button4 = QPushButton("Click me")
        button4.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Expanding)

        menus_layout = QGridLayout()


        card_types_combo_box = aqt.qt.QComboBox()
        card_types_combo_box.addItem("Korean")
        card_types_combo_box.addItem("English")
        card_types_combo_box.addItem("Mathematical Equations")

        card_types_combo_box.setFixedWidth(200)

        ai_model_version = aqt.qt.QComboBox()
        ai_model_version.addItems(["Astra", "Luna", "Sol"])

        ai_model_version.setFixedWidth(200)

        input_price_line = aqt.qt.QLineEdit()
        input_price_line.setText("Input Price")
        input_price_line.setReadOnly(True)

        output_price_line = aqt.qt.QLineEdit()
        output_price_line.setText("Output Price")
        output_price_line.setReadOnly(False)

        menus_layout.addWidget(card_types_combo_box, 0, 0, 1, 2)
        menus_layout.addWidget(ai_model_version, 1, 0, 1, 2)
        menus_layout.addWidget(input_price_line, 2, 0)
        menus_layout.addWidget(output_price_line, 2, 1)

        self.addLayout(menus_layout, 0, 0)
        self.addWidget(button2, 1, 0)
        self.addWidget(button3, 1, 1)



class NoteFieldsCheckBoxes(aqt.qt.QVBoxLayout):
    def __init__(self, fields_list: list[str]=[]):
        super().__init__()

        fields_check_boxes_container = aqt.qt.QWidget()

        fields_check_boxes_vertical_layout = aqt.qt.QVBoxLayout(fields_check_boxes_container)


        for field in fields_list:
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
    configuration_dialog = ConfigurationDialog(browser)
    configuration_dialog.exec()
