# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_translater.ui'
#
# Created: Sun Oct 09 15:33:42 2016
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_TranslateDialog(object):
    def setupUi(self, TranslateDialog):
        TranslateDialog.setObjectName("TranslateDialog")
        TranslateDialog.resize(885, 607)
        self.gridLayout = QtGui.QGridLayout(TranslateDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(TranslateDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 11, 0, 1, 1)
        self.transEdit = QtGui.QPlainTextEdit(TranslateDialog)
        self.transEdit.setObjectName("transEdit")
        self.gridLayout.addWidget(self.transEdit, 8, 1, 1, 1)
        self.filterEdit = QtGui.QLineEdit(TranslateDialog)
        self.filterEdit.setObjectName("filterEdit")
        self.gridLayout.addWidget(self.filterEdit, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtGui.QLabel(TranslateDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.dirtyBox = QtGui.QCheckBox(TranslateDialog)
        self.dirtyBox.setObjectName("dirtyBox")
        self.horizontalLayout_2.addWidget(self.dirtyBox)
        self.removeButton = QtGui.QPushButton(TranslateDialog)
        self.removeButton.setObjectName("removeButton")
        self.horizontalLayout_2.addWidget(self.removeButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 1, 1, 1)
        self.origEdit = QtGui.QPlainTextEdit(TranslateDialog)
        self.origEdit.setObjectName("origEdit")
        self.gridLayout.addWidget(self.origEdit, 8, 0, 1, 1)
        self.label_2 = QtGui.QLabel(TranslateDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 9, 0, 1, 1)
        self.label_3 = QtGui.QLabel(TranslateDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.untransOnlyBox = QtGui.QCheckBox(TranslateDialog)
        self.untransOnlyBox.setObjectName("untransOnlyBox")
        self.horizontalLayout.addWidget(self.untransOnlyBox)
        self.saveButton = QtGui.QPushButton(TranslateDialog)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        self.plainTextEdit = QtGui.QPlainTextEdit(TranslateDialog)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 10, 0, 1, 2)
        self.tableView = QtGui.QTableView(TranslateDialog)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 3, 0, 1, 2)

        self.retranslateUi(TranslateDialog)
        QtCore.QMetaObject.connectSlotsByName(TranslateDialog)

    def retranslateUi(self, TranslateDialog):
        TranslateDialog.setWindowTitle(QtGui.QApplication.translate("TranslateDialog", "Translation", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TranslateDialog", "Statistics:", None, QtGui.QApplication.UnicodeUTF8))
        self.filterEdit.setText(QtGui.QApplication.translate("TranslateDialog", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("TranslateDialog", "Translated:", None, QtGui.QApplication.UnicodeUTF8))
        self.dirtyBox.setText(QtGui.QApplication.translate("TranslateDialog", "dirty", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("TranslateDialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TranslateDialog", "Comments:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("TranslateDialog", "Original:", None, QtGui.QApplication.UnicodeUTF8))
        self.untransOnlyBox.setText(QtGui.QApplication.translate("TranslateDialog", "show untranslated only", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("TranslateDialog", "Save", None, QtGui.QApplication.UnicodeUTF8))

