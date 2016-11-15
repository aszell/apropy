# Apropy - a Java properties file editor in python.
# Copyright (C) 2016 Andras Szell

import sys
import time
import os
import os.path
import logging
from collections import OrderedDict
from ConfigParser import ConfigParser, DuplicateSectionError

from PySide.QtGui import QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QDialog, QIcon
from PySide import QtGui, QtCore

from ui_mainwindow import Ui_MainWindow
from ui_options import Ui_OptionsDialog

from prop import propread, propsave, TransItem

VERSION_STR = "apropy v0.0.2 alpha"

ININAME = 'apropy.ini'
ORIG_BASENAME = 'msg_bundle.properties'
TRANS_BASENAME = 'msg_bundle_hu.properties'
LOG_FNAME = 'apropy.log'


def error_popup(msg):
    msgBox = QMessageBox()
    msgBox.setText(msg)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setDefaultButton(QMessageBox.Ok)
    msgBox.exec_()


class TableDelegate(QtGui.QStyledItemDelegate):
    ''' 
    Custom tableView edit delegate created to properly follow the state of table view edits. 
    There were lots of other attempts but this one seems to be the only stable one
    which can tell whether the table view is currently edited, and let me close 
    the editor so the model gets the currently edited data when save is triggered
    with a shortcut. (Otherwise the currently edited line is not saved just if Enter is 
    pressed before CTRL+S.)
    Issue was that a table cell edit is a separate QLineEdit which the table does not know much about.
    '''

    def __init__(self, parent=None):
        super(TableDelegate, self).__init__(parent)
        self.closeEditor.connect(self.editorClosed)
        self.is_edited = False
        
    def createEditor(self, parent, option, index):
        self.editor = QtGui.QLineEdit(parent)
        self.is_edited = True
        return self.editor
    
    def editorClosed(self):
        self.is_edited = False
        
    def isEdited(self):
        return self.is_edited
    
    def stopEditing(self):
        self.editor.clearFocus()

    def initStyleOption(self, option, index):
        super(TableDelegate, self).initStyleOption(option, index)
        
        # first two columns can't be edited so should not be selectable
        if index.column() < 2:
            if option.state & QtGui.QStyle.State_Selected:
                option.state &= ~ QtGui.QStyle.State_Selected

class HighlightModel(QtGui.QStandardItemModel):
    def __init__(self, *args, **kwargs):
        super(HighlightModel, self).__init__(*args, **kwargs)
        self.backup = []
        
    def data(self, index, role):
        if not index.isValid():
            return None
        
        currtrans = self.item(index.row(), 2)
        itemdata = currtrans.text() if currtrans is not None else ''
        hasbackup = len(self.backup) > index.row()

        if role == QtCore.Qt.DisplayRole:
            curritem = self.item(index.row(), index.column())
            return curritem.text() if curritem is not None else ''

        if role == QtCore.Qt.TextColorRole:
            if index.column() < 2 and itemdata != "":
                # if translation text is nonempty, it's either an unsaved modification...
                if hasbackup and itemdata != self.backup[index.row()]:
                    return QtGui.QColor(0, 180, 0, 255)
                # ...or an already saved translated item
                else:
                    return QtGui.QColor(130, 130, 130, 255)
            
        # do with stylesheet instead?
        if role == QtCore.Qt.FontRole:
            if index.column() < 2:
                font = QtGui.QFont()
                font.setBold(True)
                return font
                        
        return super(HighlightModel, self).data(index, role)

    def create_checkpoint(self):
        ''' Stores all the current translations for later comparison '''
        new_backup = []

        for row in range(self.rowCount()):
            text = self.item(row, 2).text()
            
            # emit datachanges for all rows that were edited so green highlight is removed on save
            if len(self.backup) > row and text != self.backup[row]:
                self.item(row, 0).emitDataChanged()
                self.item(row, 1).emitDataChanged()
            
            new_backup.append(text)

        self.backup = new_backup
            
        logger.debug("Checkpoint contains %d items" % len(self.backup))
        
class ApropyMainWindow(Ui_MainWindow):
    def __init__(self, window, config):
        Ui_MainWindow.__init__(self)
        
        self.config = config

        self.setupUi(window)
        self.window = window
        
        self.origfname = config.get_origfname()
        self.transfname = config.get_transfname()

        self.setup_tableview()
        self.load_dict(self.origfname, self.transfname)
        self.table_select_item(0, 2) # select first translation
        self.setup_status_bar()
       
        self.create_actions()

        self.tablerefresh_from_bottom = False
        
        icon = QIcon(get_basepath('globe.png'))
        self.window.setWindowIcon(icon)
        
        self.setup_fonts()
        
    def setup_fonts(self):
        font = self.transEdit.font()
        font.setPointSize(10)
        self.transEdit.setFont(font)
        self.origEdit.setFont(font)

    def setup_tableview(self):
        # filter and model will be created only once
        self.model = HighlightModel(5, 3)
        self.filter_proxy_model = QtGui.QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterKeyColumn(3)
        self.filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.tableEditor = TableDelegate()
        self.tableView.setItemDelegate(self.tableEditor)

        self.tableView.setModel(self.filter_proxy_model)

        self.tableView.setSelectionMode(self.tableView.SingleSelection)
        self.hide_last_col()

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
        self.model.dataChanged.connect(self.on_table_data_changed)
        
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

        self.transEdit.textChanged.connect(self.on_bottom_data_changed)

        self.copyButton.clicked.connect(self.on_copy)
       
        
        # replace tab behaviour
        self.oldTableKeyPress = self.tableView.keyPressEvent
        self.tableView.keyPressEvent = self.tableKeyPress
        self.oldTransEditKeyPress = self.transEdit.keyPressEvent
        self.transEdit.keyPressEvent = self.transEditKeyPress
    
    def on_copy(self):
        self.transEdit.setPlainText(self.origEdit.toPlainText())
    
    def on_about(self):
        QMessageBox.about(self.window, "About apropy", 
            VERSION_STR + "\n\nCopyright (C) 2016 Andras Szell\nBug reports to: szell.andris@gmail.com")
    
    def on_save(self):
        # Terminate ongoing edits of table to get edited data into model (in case CTRL+S pressed)
        if self.tableEditor.isEdited():
            self.tableEditor.stopEditing()
            self.tableView.setFocus()
        
        if self.config.get_cleanup_keys():
            logger.info("Cleaning up and reordering translation keys before saving")
            self.cleanup_dict()
            
        fout = open(self.transfname, 'wb')
        count =propsave(fout, self.trans)
        fout.close()
        logger.info(self.transfname + ' saved: %d items' % count)
        
        self.model.create_checkpoint()
        
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
        config.open_options(self.window, self.on_open_done)
        
    def on_open_done(self):
        new_origfname = config.get_origfname()
        new_transfname = config.get_transfname()
        
        if new_origfname != self.origfname or new_transfname != self.transfname:
            self.origfname, self.transfname = new_origfname, new_transfname
            self.load_dict(self.origfname, self.transfname)
            self.update_status_bar()
            self.tableView.scrollToTop()
                
    def on_find(self):
        self.filterEdit.setFocus()
        
    def on_untransbox(self):
        if self.untransOnlyBox.isChecked():
            self.fill_model(include_translated=False)
        else:
            self.fill_model(include_translated=True)
            
    def update_hidden_col(self, row):
        ''' Updates the hidden fourth column used for filtering (first three cols concatenated with spaces)
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

    def on_table_data_changed(self, topleft, bottomright):
        self.edited_key = self.model.item(topleft.row(), 0).text()
        translation = self.model.item(topleft.row(), 2).text()
        self.update_translation(self.edited_key, translation)
        self.update_hidden_col(topleft.row())

        # refresh the other view of the same data
        if not self.tablerefresh_from_bottom:
            self.transEdit.blockSignals(True)
            self.update_bottom()
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
            if config.get_copy_comments():
                newkey = TransItem(key, self.origins[key].comment, translation)
            else:
                newkey = TransItem(key, '', translation)
            self.trans[key] = newkey

        self.update_status_bar()
        
    def row_updated(self, row):
        self.model.item(self.edited_row, 0).emitDataChanged()
        self.model.item(self.edited_row, 1).emitDataChanged()
            
    def table_delete_translation(self):
        if self.edited_row is not None:
            self.model.item(self.edited_row, 2).setText('')
        self.row_updated(self.edited_row)        
        
    def table_select_item(self, row, col):
        target = self.model.index(row, col)
        self.tableView.selectionModel().setCurrentIndex(target, QtGui.QItemSelectionModel.ClearAndSelect)
        self.on_sel_changed(QtGui.QItemSelection(target, target), QtGui.QItemSelection)

    def on_bottom_data_changed(self):
        self.tablerefresh_from_bottom = True
        if self.edited_row is not None:
            self.model.item(self.edited_row, 2).setText(self.transEdit.toPlainText())

        self.tablerefresh_from_bottom = False

    def update_bottom(self):
        # if nothing is selected
        if self.edited_key is None:
            self.origEdit.setPlainText('')
            self.transEdit.blockSignals(True)
            self.transEdit.setPlainText('')
            self.transEdit.blockSignals(False)
            self.commentEdit.setPlainText('')
            return

        self.origEdit.setPlainText(self.origins[self.edited_key].trans)

        if self.edited_key in self.trans:
            self.transEdit.blockSignals(True)
            self.transEdit.setPlainText(self.trans[self.edited_key].trans)
            self.transEdit.blockSignals(False)
            
            # comments: take from translated file, but if that is empty, use original file's comments
            if self.trans[self.edited_key].comment.strip():
                self.commentEdit.setPlainText(self.trans[self.edited_key].comment)
            elif self.edited_key in self.origins:
                self.commentEdit.setPlainText(self.origins[self.edited_key].comment)
        else:
            self.transEdit.blockSignals(True)
            self.transEdit.setPlainText('')
            self.transEdit.blockSignals(False)
            self.commentEdit.setPlainText(self.origins[self.edited_key].comment)

    def on_sel_changed(self, selected, deselected):
        # earlier it was possible to select multiple items, kept handling that case
        if selected.indexes():
            modelindex = selected.indexes()[0]
            keyindex = self.filter_proxy_model.index(modelindex.row(), 0)
            self.edited_key = keyindex.data()
            self.edited_row = self.filter_proxy_model.mapToSource(keyindex).row()
            self.update_bottom()
            # print "selected:", self.edited_key, self.edited_row
        else:
            self.edited_key = None
            self.edited_row = None
            self.update_bottom()
            # print "selected: nothing"

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
        self.model.setHorizontalHeaderLabels(['Key', 'Original', 'Translation'])
        self.model.endResetModel()
        
        self.hide_last_col()
        self.tableView.scrollToTop()

        self.edited_key = None
        self.edited_row = None
        self.update_bottom()

    def hide_last_col(self):
        # fixme: when model is reset, table view somehow forgets its hidden cols
        # so as a workaround it is repeatedly hidden
        self.tableView.setColumnHidden(3, True)
       
        header = self.tableView.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)
            
    def load_dict(self, origname, transname):
        # empty dict in case file read fails
        self.origins = OrderedDict() 
        self.trans = OrderedDict()

        if origname != '' and transname != '':
        
            try:
                forig = open(origname, 'rU')
                self.origins = propread(forig)
                forig.close()
                # remove leading spaces in original translation coming from 'key = translation' strings
                for k in self.origins.keys():
                    self.origins[k].trans = self.origins[k].trans.lstrip(' ')
                
            except Exception, e:
                emsg = "Error opening original file: " + origname + "\n" + str(e)
                logger.error(emsg)
                error_popup(emsg)
                
            try:
                ftrans = open(transname, 'rU')
                self.trans = propread(ftrans)
                ftrans.close()
            except Exception, e:
                emsg = "Error opening translated file: " + transname + "\n\nPython exception:\n  " + str(e)
                logger.error(emsg)
                error_popup(emsg)

        # test: use only 10 lines
        #self.origins = OrderedDict(self.origins.items()[:10])
            
        self.fill_model()
        self.model.create_checkpoint()


class MyOptionsDialog(Ui_OptionsDialog):
    def __init__(self, dialog, callback):
        Ui_OptionsDialog.__init__(self)
        self.setupUi(dialog)
        self.window = dialog
        self.window.setModal(True)
        self.create_actions()
        self.window.show()
        self.callback = callback

    def create_actions(self):
        self.openBaseButton.clicked.connect(self.on_open_base)
        self.openTransButton.clicked.connect(self.on_open_trans)
        self.okButton.clicked.connect(self.on_ok)
        self.cancelButton.clicked.connect(self.on_cancel)

    def on_ok(self):
        self.window.close()
        self.callback()
        
    def on_cancel(self):
        self.window.close()

    def check_rel_path(self, fullpath):
        ''' 
        :return: Returns original full path or relative path if file exists, or None on error 
        '''
        
        fpath = None
        
        if os.path.isfile(fullpath):
        
            if is_same_dir(os.path.dirname(fullpath), os.getcwd()):
                logger.info("File is in current work dir, keeping filename only")
                # so moving around the executable and the properties files together is possible
                fpath = os.path.basename(fullpath)
            else:
                logger.debug("Directory changed, trying to update original file path also")
                fpath = os.path.normpath(fullpath)
                
        else:
            logger.info("Selected item is not a file.")
            
        return fpath
        
    def on_open_base(self):
        fullpath, filtermask = QFileDialog(self.window).getOpenFileName(self.window, 
                                    caption="Select base/original file", dir=workdir, filter="*.properties")
        
        fpath = self.check_rel_path(fullpath)
        if fpath is not None:
            self.baseFileEdit.setText(fpath)
            logger.info("Selected base file: " + fpath)
        else:
            logger.error("Invalid base file: " + fullpath)
        
    def on_open_trans(self):
        fullpath, filtermask = QFileDialog(self.window).getOpenFileName(self.window, 
                                    caption="Select translation file", dir=workdir, filter="*.properties")

        fpath = self.check_rel_path(fullpath)
        if fpath is not None:
            self.transFileEdit.setText(fpath)
            logger.info("Selected translation file: " + fpath)
        else:
            logger.error("Invalid base file: " + fullpath)            
            
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
        was_missing = []
        
        try:
            self.add_section("files")
        except DuplicateSectionError, e:
            pass

        try:
            self.add_section("options")
        except DuplicateSectionError, e:
            pass
        

        keys = [
            ('files', 'orig', ''),
            ('files', 'trans', ''),
            ('options', 'cleanup_keys_on_save', 'False'),
            ('options', 'copy_comments', 'False')
            # bool values must be set to string to avoid 
            #    "TypeError: argument of type 'bool' is not iterable"
            # see http://stackoverflow.com/a/21485083/501814
        ]
        
        for k in keys:
            try:
                self.get(k[0], k[1])
            except:
                self.set(*k)
                was_missing.append(k[1])
            
        if was_missing:
            logger.info("Missing options filled in:" + " ".join(was_missing))
            
        return was_missing

    def open_options(self, window, callback):
        self.dialog = MyOptionsDialog(QDialog(window), self.open_options_done)
        self.dialog.baseFileEdit.setText(self.get('files', 'orig'))
        self.dialog.transFileEdit.setText(self.get('files', 'trans'))
        self.dialog.cleanupBox.setChecked(self.getboolean('options', 'cleanup_keys_on_save'))
        self.dialog.copyCommentBox.setChecked(self.getboolean('options', 'copy_comments'))
        self.callback = callback
        
    def open_options_done(self):
        # process dialog contents
        d = self.dialog
        self.set('files', 'orig', d.baseFileEdit.text())
        self.set('files', 'trans', d.transFileEdit.text())
        self.set('options', 'cleanup_keys_on_save', str(d.cleanupBox.isChecked()))
        self.set('options', 'copy_comments', str(d.copyCommentBox.isChecked()))
        
        # store changes in ini
        logger.info("Options processed")
        self.save()

        # alert the main window about the config change
        self.callback()
        
    def get_origfname(self):  return self.get('files', 'orig')
    def get_transfname(self): return self.get('files', 'trans')
    def get_cleanup_keys(self): return self.getboolean('options', 'cleanup_keys_on_save')
    def get_copy_comments(self): return self.getboolean('options', 'copy_comments')

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

def get_basepath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)        

def setup_logging():
    logger = logging.getLogger("apropy")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    ch = logging.FileHandler(LOG_FNAME)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger
    
if __name__ == "__main__":
    config = MyConfig()
    workdir = '.'
    
    logger = setup_logging()
    
    logger.info("Logging to " + LOG_FNAME)
    logger.info(VERSION_STR + " started")
    
    if os.path.isfile(ININAME):
        config.load(ININAME)
    else:
        logger.warn("Unable to read ini file, creating...")
        config.init_missing()
        config.save(ININAME)
  

    app = QApplication(sys.argv)
    window = QMainWindow()
    awindow = ApropyMainWindow(window, config)
    window.show()
  
    sys.exit(app.exec_())
