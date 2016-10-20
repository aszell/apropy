import sys

from ConfigParser import ConfigParser, DuplicateSectionError

from PySide.QtGui import QApplication, QDialog, QFileDialog, QTextCursor, QSystemTrayIcon, QIcon, QMenu, QAction, qApp, QCursor, QDesktopServices
from PySide.QtCore import QTimer, QProcess, QUrl
from PySide import QtCore

from ui_translater import Ui_TranslateDialog

ININAME = "translater.ini"

class TranslateDialog(Ui_TranslateDialog):
    def __init__(self, window):
        Ui_TranslateDialog.__init__(self)
        
        self.window = window
        self.setupUi(window)

if __name__ == "__main__":        
    config = ConfigParser()
    try:
        config.read(ININAME)
    except Exception, e:
        print e
    
    app = QApplication(sys.argv)
    window = QDialog()
    
    ui = TranslateDialog(window)
    window.show()
        
    sys.exit(app.exec_())
