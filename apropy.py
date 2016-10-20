import sys
import time
from collections import OrderedDict

from ConfigParser import ConfigParser, DuplicateSectionError

from PySide.QtGui import QApplication, QMainWindow, QWidget, QDialog, QFileDialog, QTextCursor, QSystemTrayIcon, QIcon, QMenu, QAction, qApp, QCursor, QDesktopServices
from PySide import QtGui
from PySide.QtCore import QTimer, QProcess, QUrl
from PySide import QtCore

from ui_mainwindow import Ui_MainWindow

from prop import propread, propsave, TransItem

ININAME = "translater.ini"

class ApropyMainWindow(Ui_MainWindow):
    def __init__(self, window, origname, transname):
        Ui_MainWindow.__init__(self)

        self.setupUi(window)
        self.window = window
        
        self.origfname = origname
        self.transfname = transname
        
        self.create_dict(origname, transname)
        self.setup_status_bar()
        
        self.create_actions()

        self.tablerefresh_from_bottom = False

    def setup_status_bar(self):
        self.window.statusBar().showMessage('Translated:')

        self.progressText = QtGui.QLabel('')
        self.progressBar = QtGui.QProgressBar()
        self.window.statusBar().addPermanentWidget(self.progressText)
        self.window.statusBar().addPermanentWidget(self.progressBar)

        self.progressBar.setGeometry(30, 40, 200, 25)

        self.update_status_bar()

    def update_status_bar(self):
        orig_keycnt = len(self.origins)
        trans_keycnt = len(self.trans)
        self.progressBar.setValue(trans_keycnt * 100 / orig_keycnt)
        self.progressText.setText('%d / %d' % (trans_keycnt, orig_keycnt))

    def tableKeyPress(self, event):
        ''' Key bindings are hacked so a TAB press on table does not go to next cell but
            switch between the detailed bottom editbox and table. '''
        if event.key() == QtCore.Qt.Key_Tab:
            event.ignore()
        else:
            self.oldTableKeyPress(event)

    def transEditKeyPress(self, event):
        ''' Bottom edit box should not accept TABs but instead window should switch to
            translation table '''
        if event.key() == QtCore.Qt.Key_Tab:
            event.ignore()
        else:
            self.oldTransEditKeyPress(event)

    def create_actions(self):
        self.model.dataChanged.connect(self.table_data_changed)
        
        self.action_Save.setShortcut('Ctrl+S')
        self.action_Save.setStatusTip('Save translated file')
        self.action_Save.triggered.connect(self.on_save)
        self.action_Open.setShortcut('Ctrl+O')
        self.action_Open.setStatusTip('Open translation')
        self.action_Open.triggered.connect(self.on_open)
        
        findShortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), self.window)
        findShortcut.activated.connect(self.on_find)

        self.filterEdit.textChanged.connect(self.filter_proxy_model.setFilterFixedString)
        self.untransOnlyBox.clicked.connect(self.on_untransbox)
        selMode = self.tableView.selectionModel()
        selMode.selectionChanged.connect(self.on_sel_changed)

        self.transEdit.textChanged.connect(self.bottom_data_changed)

        # replace tab behaviour
        self.oldTableKeyPress = self.tableView.keyPressEvent
        self.tableView.keyPressEvent = self.tableKeyPress
        self.oldTransEditKeyPress = self.transEdit.keyPressEvent
        self.transEdit.keyPressEvent = self.transEditKeyPress
        
    def on_save(self):
        fout = open(self.transfname, 'wb')
        propsave(fout, self.trans)
        fout.close()
        print "Saved"
        
    def on_open(self):
        global workdir
        print "Open"
        fullpath, filtermask = QFileDialog(self.window).getOpenFileName(self.window, 
                                    caption="cap", dir=workdir, filter="*.properties")

        old_transfname = self.transfname
        try:
            self.transfname = fullpath
            self.create_dict(self.origfname, self.transfname)
            self.update_status_bar()
            self.tableView.scrollToTop()
        except Exception, e:
            print "Exception hit:", e            
            self.transfname = old_transfname
        
    def on_find(self):
        self.filterEdit.setFocus()

    def on_untransbox(self):
        if self.untransOnlyBox.isChecked():
            self.fill_model(include_translated=False)
        else:
            self.fill_model(include_translated=True)
            
        print self.filter_proxy_model.rowCount()            

    def update_hidden_col(self, row):
        ''' Updates the hidden fourth column used for filtering (all texts together)
        :param topleft: model index for the row whose hidden column is to be updated
        '''
        item_key = self.model.item(row, 0)
        item_orig = self.model.item(row, 1)
        item_trans = self.model.item(row, 2)
        itext = ' '.join([item_key.text(), item_orig.text(), item_trans.text()])
        item_all = QtGui.QStandardItem(itext)
        signalsBlocked = self.model.signalsBlocked()
        self.model.blockSignals(True)
        self.model.setItem(row, 3, item_all)
        self.model.blockSignals(signalsBlocked)

    def table_data_changed(self, topleft, bottomright):
        key = self.model.item(topleft.row(), 0).text()
        translation = self.model.item(topleft.row(), 2).text()
        self.update_translation(key, translation)
        self.update_hidden_col(topleft.row())

        # refresh the other view of the same data
        if not self.tablerefresh_from_bottom:
            self.transEdit.blockSignals(True)
            self.update_bottom(key)
            self.transEdit.blockSignals(False)

    def update_translation(self, key, translation):
        if key in self.trans:
            if not translation.strip(): # empty string
                self.trans.pop(key)
            else:
                self.trans[key].trans = translation                
        elif translation.strip():
            newkey = TransItem(key, self.origins[key].comment, translation)
            self.trans[key] = newkey
            # put it in the same position as in the original translation
            newOrder = OrderedDict()
            for k in self.origins.keys():
                if k in self.trans:
                    newOrder[k] = self.trans[k]

            self.trans = newOrder

        self.update_status_bar()

    def bottom_data_changed(self):
        # the way I get to model item from filtered table row is obviously overcomplicated
        # fix it please...
        self.tablerefresh_from_bottom = True
        selected = self.tableView.selectedIndexes()
        if selected: # if nothing selected, text gets lost?
            fp = self.filter_proxy_model
            model_idx = fp.mapToSource(fp.index(selected[0].row(), 0))
            key = self.model.itemFromIndex(model_idx).text()
            #self.update_translation(key, self.transEdit.toPlainText())
            # refresh the other view of the same data
            #print 'bott-updatetable'
            #self.update_table(self.transEdit.toPlainText())
            #print "Updating row", model_idx.row()
            self.model.item(model_idx.row(), 2).setText(self.transEdit.toPlainText())

        self.tablerefresh_from_bottom = False

    def update_bottom(self, key):
        self.origEdit.setPlainText(self.origins[key].trans)
        if key in self.trans:
            self.transEdit.blockSignals(True)
            self.transEdit.setPlainText(self.trans[key].trans)
            self.transEdit.blockSignals(False)
            self.commentEdit.setPlainText(self.trans[key].comment)
        else:
            self.transEdit.blockSignals(True)
            self.transEdit.setPlainText('')
            self.transEdit.blockSignals(False)
            self.commentEdit.setPlainText(self.origins[key].comment)

    def on_sel_changed(self, topleft, bottomright):
        modelindex = topleft.indexes()[0]
        keyindex = self.filter_proxy_model.index(modelindex.row(), 0)
        key = keyindex.data()
        self.update_bottom(key)

    def fill_model(self, include_translated=True, **kwargs):
        old_rowcnt = self.model.rowCount()

        # beginResetModel - endResetModel is required to get the number of displayed table
        # rows be properly updated
        self.model.beginResetModel()
        self.model.clear()
        self.model.blockSignals(True)
        
        row = 0
        for idx, tr in enumerate(self.origins.values()):
            # skip lines with existing translation if 'untranslated only' selected
            if tr.key in self.trans and not include_translated:
                continue

            item_key = QtGui.QStandardItem(tr.key)
            item_key.setFlags(item_key.flags() & ~QtCore.Qt.ItemIsEditable)
            item_orig = QtGui.QStandardItem(tr.trans)
            item_orig.setFlags(item_orig.flags() & ~QtCore.Qt.ItemIsEditable)

            if tr.key in self.trans:
                item_trans = QtGui.QStandardItem(self.trans[tr.key].trans)
            else:
                item_trans = QtGui.QStandardItem('')

            item_all = QtGui.QStandardItem(' '.join([item_key.text(), item_orig.text(), item_trans.text()]))

            self.model.setItem(row, 0, item_key)
            self.model.setItem(row, 1, item_orig)
            self.model.setItem(row, 2, item_trans)
            self.model.setItem(row, 3, item_all)
            row += 1

        # without blocking the signals we'd receive lots of errors 
        # as the translation updates would be triggered on data change        
        self.model.blockSignals(False)
        
        self.model.endResetModel()
        self.hide_last_col()

    def hide_last_col(self):
        # fixme: when model is reset, table view somehow forgets its hidden cols
        # so as a workaround it is repeatedly hidden
        self.tableView.setColumnHidden(3, True)
       
        header = self.tableView.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)
            
    def create_dict(self, origname, transname):
        forig = open(origname, 'rU')
        ftrans = open(transname, 'rU')
        self.origins = propread(forig)
        self.trans = propread(ftrans)
        forig.close()
        ftrans.close()

        self.model = QtGui.QStandardItemModel(5, 3)
        self.model.setHorizontalHeaderLabels(['ID', 'English', 'Translated'])

        self.fill_model()

        self.filter_proxy_model = QtGui.QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterKeyColumn(3)
        self.filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.tableView.setModel(self.filter_proxy_model)
        self.hide_last_col()


if __name__ == "__main__":
    config = ConfigParser()
    origfname = 'msg_bundle.properties'
    transfname = 'msg_bundle_hu.properties'
    try:
        workdir = 'w:\\langer\\'
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
    window = QMainWindow()
    awindow = ApropyMainWindow(window, origfname, transfname)
    window.show()
    
    sys.exit(app.exec_())
