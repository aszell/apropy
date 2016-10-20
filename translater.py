import sys

from ConfigParser import ConfigParser, DuplicateSectionError

from PySide.QtGui import QApplication, QMainWindow, QDialog, QFileDialog, QTextCursor, QSystemTrayIcon, QIcon, QMenu, QAction, qApp, QCursor, QDesktopServices
from PySide import QtGui
from PySide.QtCore import QTimer, QProcess, QUrl
from PySide import QtCore

from ui_translater import Ui_TranslateDialog

from prop import propread, propsave, TransItem

ININAME = "translater.ini"

class TranslateDialog(Ui_TranslateDialog):
    def __init__(self, window, origname, transname):
        Ui_TranslateDialog.__init__(self)
        
        self.window = window
        self.setupUi(window)

        self.origfname = origname
        self.transfname = transname
        self.fill_dict(origname, transname)

        self.create_actions()

    def create_actions(self):
        self.saveButton.clicked.connect(self.on_save)
        self.model.dataChanged.connect(self.data_changed)
        saveShortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self.window)
        saveShortcut.activated.connect(self.on_save)

    def on_save(self):
        fout = open(self.transfname, 'wb')
        propsave(fout, self.trans)
        print "Saved"

    def fill_dict(self, origname, transname):
        forig = open(origname, 'rU')
        ftrans = open(transname, 'rU')
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

    def data_changed(self, topleft, bottomright):
        key = self.model.item(topleft.row(), 0).text()
        if key in self.trans:
            self.trans[key].trans = self.model.item(topleft.row(), 2).text()
        else:
            newkey = TransItem(key, self.origins[key].comment, self.model.item(topleft.row(), 2).text())
            #print newkey
            #print len(self.trans)
            self.trans[key] = newkey
            #print len(self.trans)

if __name__ == "__main__":
    config = ConfigParser()
    origfname = 'msg_bundle.properties'
    transfname = 'msg_bundle_hu.properties'
    try:
        config.read(ININAME)

        origfname  = config.get('trans', 'orig')
        transfname = config.get('trans', 'trans')
    except Exception, e:
        try:
            config.add_section("trans")
            print "Unable to read ini file, creating"
        except DuplicateSectionError, e:
            has_ini = True
            print "Extending former ini file"
            
        config.set('trans', 'orig', origfname)
        config.set('trans', 'trans', 'msg_bundle_hu.properties')

        with open(ININAME, 'wb') as configfile:
            config.write(configfile)

    app = QApplication(sys.argv)
    window = QDialog()
    
    ui = TranslateDialog(window, origfname, transfname)
    window.show()
        
    sys.exit(app.exec_())
