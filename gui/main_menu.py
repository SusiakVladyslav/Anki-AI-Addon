import aqt
from aqt import mw

from .api_keys_configuration import ApiKeysConfigurationDialog

def open_api_key_configuration_dialog() -> None:
    api_keys_configuration_dialog = ApiKeysConfigurationDialog(mw)
    api_keys_configuration_dialog.open()

def setup_tools_menu() -> None:
    action = aqt.qt.QAction("Configure API Keys", mw)
    aqt.qt.qconnect(action.triggered, open_api_key_configuration_dialog)
    mw.form.menuTools.addAction(action)
