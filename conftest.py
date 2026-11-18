import sys
from unittest.mock import MagicMock

anki_mock = MagicMock()
aqt_mock = MagicMock()
qt_mock = MagicMock()
aqt_mock.qt = qt_mock

class DummyQDialog:
    def __init__(self, parent=None):
        pass

    def resize(self, w, h): pass
    def setModal(self, modal): pass
    def setSizeGripEnabled(self, enabled): pass
    def setWindowTitle(self, title): pass
    def findChildren(self, cls): return []
    def accept(self): pass
    def reject(self): pass


class DummyQWidget:
    def __init__(self, parent=None):
        pass

    def setStyleSheet(self, style): pass
    def setToolTip(self, tip): pass
    def setFixedWidth(self, w): pass
    def setFixedHeight(self, h): pass
    def findChildren(self, cls): return []

    def __getattr__(self, name:str):
        return MagicMock()


qt_mock.QDialog = DummyQDialog
qt_mock.QWidget = DummyQWidget
qt_mock.QComboBox = DummyQWidget
qt_mock.QTabWidget = DummyQWidget
qt_mock.QTableWidget = DummyQWidget
qt_mock.QGridLayout = DummyQWidget

# 2. Qt widgets instantiated directly inside __init__ (each call gets an isolated MagicMock)
for widget_name in (
    "QDialogButtonBox",
    "QCheckBox",
    "QLabel",
    "QLineEdit",
    "QPlainTextEdit",
    "QPushButton",
    "QTableWidgetItem",
    "QGraphicsOpacityEffect",
):
    setattr(qt_mock, widget_name, MagicMock(side_effect=lambda *args, **kwargs: MagicMock()))

qt_mock.pyqtSignal = lambda *args, **kwargs: MagicMock()

mw_mock = MagicMock()
mw_mock.addonManager.addon_from_module.return_value = "ankiaddon"
aqt_mock.mw = mw_mock

sys.modules["anki"] = anki_mock
sys.modules["anki.hooks"] = anki_mock.hooks
sys.modules["anki.notes"] = anki_mock.notes
sys.modules["aqt"] = aqt_mock
sys.modules["aqt.qt"] = qt_mock
sys.modules["aqt.utils"] = aqt_mock.utils
sys.modules["aqt.sound"] = aqt_mock.sound
sys.modules["aqt.browser"] = aqt_mock.browser
sys.modules["aqt.theme"] = aqt_mock.theme
sys.modules["aqt.operations"] = aqt_mock.operations

