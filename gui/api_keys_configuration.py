import aqt
from aqt import mw

from . import gui_utils
from ..utils.constants import EYE_ICON_PATH, EYE_OFF_ICON_PATH, OPENAI_ICON_PATH, CONFIG, AVAILABLE_COMPANIES, ADDON_PACKAGE

class ApiKeysConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Configure API Key")
        self.resize(450, 300)
        self.setModal(False)

        grid = aqt.qt.QGridLayout(self)

        self.companies_tab = aqt.qt.QTabWidget()

        self._create_companies_widgets()
        self._get_companies_api_keys()
        self.fill_line_edits_with_api_keys()

        self.commit_buttons_box = aqt.qt.QDialogButtonBox(
            aqt.qt.QDialogButtonBox.StandardButton.Save
            | aqt.qt.QDialogButtonBox.StandardButton.Cancel
        )
        self.save_button = self.commit_buttons_box.button(aqt.qt.QDialogButtonBox.StandardButton.Save)
        self.save_button.setEnabled(False)

        self.commit_buttons_box.rejected.connect(self.reject)
        self.commit_buttons_box.accepted.connect(self._save_api_keys)

        grid.addWidget(self.companies_tab, 0, 0, 1, 2)
        grid.addWidget(self.commit_buttons_box, 1, 1, 1, 1)

    def _create_companies_widgets(self) -> None:
        self.companies_widgets = dict()

        for company_name in AVAILABLE_COMPANIES:
            company_tab_widget = CompanyTabWidget(company_name=company_name)
            self.companies_widgets[company_name] = company_tab_widget

            company_icon = gui_utils.get_company_icon(company_name)

            self.companies_tab.addTab(company_tab_widget, company_icon, company_name)

    def _get_companies_api_keys(self):
        self.companies_api_keys = dict()

        for company_name in AVAILABLE_COMPANIES:
            api_key = gui_utils.convert_company_name_to_api_key(company_name)
            self.companies_api_keys[api_key] = CONFIG[api_key]

    def fill_line_edits_with_api_keys(self) -> None:
        for company_name, company_tab_widget in self.companies_widgets.items():
            api_key = gui_utils.convert_company_name_to_api_key(company_name)
            company_tab_widget.line_edit.setText(self.companies_api_keys[api_key])
            company_tab_widget.line_edit.textChanged.connect(self._on_line_edit_changed)

    def _on_line_edit_changed(self) -> None:
        is_changed = self.companies_api_keys != self._collect_current_api_keys()
        self.save_button.setEnabled(is_changed)

    def _collect_current_api_keys(self) -> dict[str, str]:
        current_api_keys = dict()
        for company_name, company_widget in self.companies_widgets.items():
            api_key = gui_utils.convert_company_name_to_api_key(company_name)
            current_api_keys[api_key] = company_widget.line_edit.text().strip()

        return current_api_keys

    def _save_api_keys(self) -> None:
        if CONFIG:
            CONFIG.update(self._collect_current_api_keys())

        mw.addonManager.writeConfig(ADDON_PACKAGE, CONFIG)
        self.accept()

    def reject(self) -> None:
        if self.confirm_line_edits_changes_discard():
            super().reject()

    def confirm_line_edits_changes_discard(self) -> bool:
        if self.companies_api_keys != self._collect_current_api_keys():
            return aqt.utils.askUser(
                "You have unsaved changes. Discard them and close?",
                parent=self,
                title="Unsaved Changes"
            )
        else:
            return True


class CompanyTabWidget(aqt.qt.QWidget):
    def __init__(self, company_name: str, parent=None):
        super().__init__(parent)
        self.company_name = company_name

        self.v_layout = aqt.qt.QVBoxLayout(self)
        self.v_layout.setSpacing(5)  # Small tight spacing between label and input
        self.v_layout.setContentsMargins(10, 10, 10, 10)

        # Top stretch pushes content down to the middle
        self.v_layout.addStretch(1)

        self.enter_api_key_label = aqt.qt.QLabel(f"Enter {self.company_name} API Key")
        self.line_edit: aqt.qt.QLineEdit = aqt.qt.QLineEdit()
        self.line_edit.setEchoMode(aqt.qt.QLineEdit.EchoMode.Password)

        anki_text_color = aqt.mw.palette().color(aqt.qt.QPalette.ColorRole.Text)
        self.eye_icon: aqt.qt.QIcon = gui_utils.get_colored_icon(EYE_ICON_PATH, anki_text_color)
        self.eye_off_icon: aqt.qt.QIcon = gui_utils.get_colored_icon(EYE_OFF_ICON_PATH, anki_text_color)

        self._add_line_edit_visibility_toggle()

        self.v_layout.addWidget(self.enter_api_key_label)
        self.v_layout.addWidget(self.line_edit)

        # Bottom stretch pushes content up to the middle
        self.v_layout.addStretch(4)

    def _add_line_edit_visibility_toggle(self):
        self.visibility_toggle_action = aqt.qt.QAction(self.eye_icon, "Show API Key", self.line_edit)
        self.visibility_toggle_action.triggered.connect(self.change_visibility)
        self.line_edit.addAction(self.visibility_toggle_action, aqt.qt.QLineEdit.ActionPosition.TrailingPosition)

    def change_visibility(self):
        if self.line_edit.echoMode() == aqt.qt.QLineEdit.EchoMode.Password:
            self.line_edit.setEchoMode(aqt.qt.QLineEdit.EchoMode.Normal)
            self.visibility_toggle_action.setIcon(self.eye_off_icon)
            self.visibility_toggle_action.setToolTip("Hide API Key")
        else:
            self.line_edit.setEchoMode(aqt.qt.QLineEdit.EchoMode.Password)
            self.visibility_toggle_action.setIcon(self.eye_icon)
            self.visibility_toggle_action.setToolTip("Show API Key")