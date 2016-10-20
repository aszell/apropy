import sys

from ConfigParser import ConfigParser, DuplicateSectionError

from PySide.QtGui import QApplication, QMainWindow, QDialog, QFileDialog, QTextCursor, QSystemTrayIcon, QIcon, QMenu, QAction, qApp, QCursor, QDesktopServices
from PySide import QtGui
from PySide.QtCore import QTimer, QProcess, QUrl
from PySide import QtCore

from ui_translater import Ui_TranslateDialog

from prop import propread

ININAME = "translater.ini"

class TranslateDialog(Ui_TranslateDialog):
    def __init__(self, window):
        Ui_TranslateDialog.__init__(self)
        
        self.window = window
        self.setupUi(window)

        self.fill_dict()

    def fill_dict(self):
        forig = open('msg_bundle.properties', 'rU')
        ftrans = open('msg_bundle_hu.properties', 'rU')
        self.origins = propread(forig)
        self.trans = propread(ftrans)

        self.model = QtGui.QStandardItemModel(5, 3)
        self.model.setHorizontalHeaderLabels(['ID', 'English', 'Translated'])

        for idx, tr in enumerate(self.origins.values()):
            item_key = QtGui.QStandardItem(tr.key)
            item_key.setFlags(item_key.flags() & ~QtCore.Qt.ItemIsEditable)
            item_orig = QtGui.QStandardItem(tr.trans)
            item_orig.setFlags(item_orig.flags() & ~QtCore.Qt.ItemIsEditable)
            if tr.key in self.trans:
                item_trans = QtGui.QStandardItem(self.trans[tr.key].trans)
            else:
                item_trans = QtGui.QStandardItem('')

            self.model.setItem(idx, 0, item_key)
            self.model.setItem(idx, 1, item_orig)
            self.model.setItem(idx, 2, item_trans)

        filter_proxy_model = QtGui.QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(self.model)
        filter_proxy_model.setFilterKeyColumn(1) # third column

        self.tableView.setModel(filter_proxy_model)

        header = self.tableView.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)

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
