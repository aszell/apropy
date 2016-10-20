import sys
import time
import os
import os.path
import logging
from collections import OrderedDict
from ConfigParser import ConfigParser, DuplicateSectionError

from PySide.QtGui import QApplication, QMainWindow, QWidget, QDialog, QFileDialog, QTextCursor, QSystemTrayIcon, QIcon, QMenu, QAction, qApp, QCursor, QDesktopServices, QMessageBox
from PySide import QtGui
from PySide.QtCore import QTimer, QProcess, QUrl
from PySide import QtCore

from ui_mainwindow import Ui_MainWindow

from prop import propread, propsave, TransItem

VERSION_STR = "apropy v0.01"

ININAME = 'apropy.ini'
ORIG_BASENAME = 'msg_bundle.properties'
TRANS_BASENAME = 'msg_bundle_hu.properties'
LOG_FNAME = 'apropy.log'

class ApropyMainWindow(Ui_MainWindow):
    def __init__(self, window, config):
        Ui_MainWindow.__init__(self)
        
        self.config = config

        self.setupUi(window)
        self.window = window
        
        self.origfname = config.get_origfname()
        self.transfname = config.get_transfname()
        
        self.create_dict(self.origfname, self.transfname)
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
        if orig_keycnt > 0:
            self.progressBar.setValue(trans_keycnt * 100 / orig_keycnt)
            self.progressText.setText('%d / %d' % (trans_keycnt, orig_keycnt))

    def tableKeyPress(self, event):
        ''' Key bindings are hacked so a TAB press on table does not go to next cell but
            switch between the detailed bottom editbox and table. '''
        if event.key() == QtCore.Qt.Key_Tab:
            event.ignore()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.table_delete_translation()
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
        
        self.action_About.triggered.connect(self.on_about)
        
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
    
    def on_about(self):
        msgBox = QMessageBox()
        msgBox.setText(VERSION_STR)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()
    
    def on_save(self):
        if self.config.get_cleanup_keys():
            logger.info("Cleaning up and reordering translation keys before saving")
            self.cleanup_dict()
            
        fout = open(self.transfname, 'wb')
        count =propsave(fout, self.trans)
        fout.close()
        logger.info(self.transfname + ' saved: %d items' % count)
        
    def ask_for_basedir_change(self):
        msgBox = QMessageBox()
        msgBox.setText("Found a " + ORIG_BASENAME + " file in the translated file's directory.")
        msgBox.setInformativeText("Use that as a base file?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        ret = msgBox.exec_()
        if ret == QMessageBox.Yes:
            return True
        elif ret == QMessageBox.No:
            return False
                
    def on_open(self):
        global workdir
        fullpath, filtermask = QFileDialog(self.window).getOpenFileName(self.window, 
                                    caption="cap", dir=workdir, filter="*.properties")

        logger.info("Opening file: " + fullpath)
        old_transfname = self.transfname
        old_origfname = self.origfname
        
        if os.path.isfile(fullpath):
        
            if is_same_dir(os.path.dirname(fullpath), os.getcwd()):
                logger.info("File is in current work dir, keeping filename only")
                self.transfname = os.path.basename(fullpath)
                new_origfname = ORIG_BASENAME
            else:
                logger.info("Translated file directory changed, trying to update original file path also")
                self.transfname = os.path.normpath(fullpath)
                
                new_origfname = os.path.join(os.path.dirname(fullpath), ORIG_BASENAME)
                                            
            if os.path.isfile(new_origfname) and not is_same_dir(new_origfname, self.origfname):
                if self.ask_for_basedir_change():
                    self.origfname = os.path.normpath(new_origfname)
            
            try:
                self.create_dict(self.origfname, self.transfname)
                self.update_status_bar()
                self.tableView.scrollToTop()
            except Exception, e:
                logger.error("Exception hit:" + str(e))
                self.transfname = old_transfname
                self.origfnaem = old_origfname
        else:
            logger.info("Selected item is not a file.")
        
        if old_transfname != self.transfname:
            config_update_filenames(self.origfname, self.transfname)
        
    def on_find(self):
        self.filterEdit.setFocus()

    def on_untransbox(self):
        if self.untransOnlyBox.isChecked():
            self.fill_model(include_translated=False)
        else:
            self.fill_model(include_translated=True)
            
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
            
    def cleanup_dict(self):
        # reorder translated strings to match original translation,
        # delete obsolete keys
        newOrder = OrderedDict()
        for k in self.origins.keys():
            if k in self.trans:
                newOrder[k] = self.trans[k]

        self.trans = newOrder
        
        self.update_status_bar()

    def update_translation(self, key, translation):
        if key in self.trans:
            if not translation.strip(): 
                # empty string entered -> delete translation entry
                self.trans.pop(key)
            else:
                self.trans[key].trans = translation                
        elif translation.strip():
            newkey = TransItem(key, self.origins[key].comment, translation)
            self.trans[key] = newkey

        self.update_status_bar()

    def get_selected_row(self):
        # fixme: the way I get to model item from filtered table row is obviously overcomplicated

        selected = self.tableView.selectedIndexes()
        if selected: # if nothing selected, text gets lost?
            fp = self.filter_proxy_model
            model_idx = fp.mapToSource(fp.index(selected[0].row(), 0))
            return model_idx.row()
        else:
            return None
        
    def table_delete_translation(self):
        row = self.get_selected_row()
        if row is not None:
            self.model.item(row, 2).setText('')

    def bottom_data_changed(self):
        self.tablerefresh_from_bottom = True
        row = self.get_selected_row()
        if row is not None:
            self.model.item(row, 2).setText(self.transEdit.toPlainText())

        self.tablerefresh_from_bottom = False

    def update_bottom(self, key):
        self.origEdit.setPlainText(self.origins[key].trans)

        if key in self.trans:
            self.transEdit.blockSignals(True)
            self.transEdit.setPlainText(self.trans[key].trans)
            self.transEdit.blockSignals(False)
            
            # comments: take from translated file, but if that is empty, use original file's comments
            if self.trans[key].comment.strip():
                self.commentEdit.setPlainText(self.trans[key].comment)
            elif key in self.origins:
                self.commentEdit.setPlainText(self.origins[key].comment)
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
        self.model.blockSignals(True)
        self.model.clear()
        
        row = 0

        for tr in self.origins.values():
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
        
        # endResetModel must be able to emit signals so filter gets updated
        
        self.model.endResetModel()
        
        self.hide_last_col()
        self.tableView.scrollToTop()

    def hide_last_col(self):
        # fixme: when model is reset, table view somehow forgets its hidden cols
        # so as a workaround it is repeatedly hidden
        self.tableView.setColumnHidden(3, True)
       
        header = self.tableView.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)
            
    def create_dict(self, origname, transname):
        self.origins = OrderedDict()
        self.trans = OrderedDict()
        try:
            forig = open(origname, 'rU')
            self.origins = propread(forig)
            forig.close()
        except Exception, e:
            logger.error("Error opening original file: " + origname)
            logger.error(str(e))
            
        try:
            ftrans = open(transname, 'rU')
            self.trans = propread(ftrans)
            ftrans.close()
        except Exception, e:
            logger.error("Error opening translated file: " + transname)
            logger.error(str(e))

        self.model = QtGui.QStandardItemModel(5, 3)
        self.model.setHorizontalHeaderLabels(['ID', 'English', 'Translated'])

        self.fill_model()

        self.filter_proxy_model = QtGui.QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterKeyColumn(3)
        self.filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.tableView.setModel(self.filter_proxy_model)

        #self.tableView.setSelectionBehaviour(self.tableView.SelectItems)
        self.tableView.setSelectionMode(self.tableView.SingleSelection)

        
        self.hide_last_col()
        
class MyConfig(ConfigParser, object):
    def __init__(self):
        ConfigParser.__init__(self)
        self.fname = ININAME

    def load(self, ininame):
        self.read(ininame)
        self.fname = ininame
        if self.init_missing():
            self.save()
    
    def save(self, fname=None):
        if fname is not None:
            self.fname = fname
        with open(self.fname, 'wb') as configfile:
            self.write(configfile)
            logger.info("Saved config: " + self.fname)

    def init_missing(self):
        was_missing = False
        
        try:
            self.add_section("files")
            was_missing = True
        except DuplicateSectionError, e:
            pass

        try:
            self.add_section("options")
            was_missing = True
        except DuplicateSectionError, e:
            pass
            
        try:
            self.get('files', 'orig')
        except:
            self.set('files', 'orig', ORIG_BASENAME)
            was_missing = True
            
        try:
            self.get('files', 'trans')
        except:
            self.set('files', 'trans', TRANS_BASENAME)
            was_missing = True

        try:
            self.get('options', 'cleanup_keys_on_save')
        except:
            # bool values must be set to string to avoid 
            #    "TypeError: argument of type 'bool' is not iterable"
            # see http://stackoverflow.com/a/21485083/501814
            self.set('options', 'cleanup_keys_on_save', 'True')
            was_missing = True

        try:
            self.get('options', 'log_to_file')
        except:
            self.set('options', 'log_to_file', 'False')
            was_missing = True
            
        if was_missing:
            logger.info("Missing options filled in")
            
        return was_missing

    def get_origfname(self):  return self.get('files', 'orig')
    def set_origfname(self, value):  self.set('files', 'orig', value)
    
    def get_transfname(self): return self.get('files', 'trans')
    def set_transfname(self, value): self.set('files', 'trans', value)
    
    # these params are not exposed, edit ini directly
    def get_cleanup_keys(self): return self.getboolean('options', 'cleanup_keys_on_save')
    def get_log_to_file(self): return self.getboolean('options', 'log_to_file')

def config_update_filenames(new_orig, new_trans):
    config.set_origfname(new_orig)
    config.set_transfname(new_trans)
    config.save()

def is_same_dir(first, second):
    # should be using os.path.samefile(path1, path2) under Unix...
    # should be making lower case on Windows
    rel1, rel2 = first, second
    try:
        rel1 = os.path.relpath(first)
    except:
        pass
        
    try:
        rel2 = os.path.relpath(second)
    except:
        pass
        
    rel1, rel2 = os.path.normpath(rel1), os.path.normpath(rel2)
    #print rel1, rel2
    return rel1 == rel2

if __name__ == "__main__":
    config = MyConfig()
    workdir = '.'
    
    logger = logging.getLogger("apropy")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info(VERSION_STR + " started")
    
    if os.path.isfile(ININAME):
        config.load(ININAME)
    else:
        logger.warn("Unable to read ini file, creating...")
        config.init_missing()
        config.save(ININAME)
        
    if config.get_log_to_file():
        ch = logging.FileHandler(LOG_FNAME)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        logger.info("Logging to " + LOG_FNAME)

    app = QApplication(sys.argv)
    window = QMainWindow()
    awindow = ApropyMainWindow(window, config)
    window.show()
    
    sys.exit(app.exec_())
