# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_options.ui'
#
# Created: Wed Oct 26 19:40:39 2016
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_OptionsDialog(object):
    def setupUi(self, OptionsDialog):
        OptionsDialog.setObjectName("OptionsDialog")
        OptionsDialog.resize(594, 256)
        self.verticalLayout = QtGui.QVBoxLayout(OptionsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.fileBox = QtGui.QGroupBox(OptionsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileBox.sizePolicy().hasHeightForWidth())
        self.fileBox.setSizePolicy(sizePolicy)
        self.fileBox.setObjectName("fileBox")
        self.gridLayout = QtGui.QGridLayout(self.fileBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.fileBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.baseFileEdit = QtGui.QLineEdit(self.fileBox)
        self.baseFileEdit.setObjectName("baseFileEdit")
        self.gridLayout.addWidget(self.baseFileEdit, 0, 1, 1, 1)
        self.openBaseButton = QtGui.QPushButton(self.fileBox)
        self.openBaseButton.setObjectName("openBaseButton")
        self.gridLayout.addWidget(self.openBaseButton, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.fileBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.transFileEdit = QtGui.QLineEdit(self.fileBox)
        self.transFileEdit.setObjectName("transFileEdit")
        self.gridLayout.addWidget(self.transFileEdit, 1, 1, 1, 1)
        self.openTransButton = QtGui.QPushButton(self.fileBox)
        self.openTransButton.setObjectName("openTransButton")
        self.gridLayout.addWidget(self.openTransButton, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.fileBox)
        self.optionsBox = QtGui.QGroupBox(OptionsDialog)
        self.optionsBox.setObjectName("optionsBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.optionsBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cleanupBox = QtGui.QCheckBox(self.optionsBox)
        self.cleanupBox.setToolTip("")
        self.cleanupBox.setObjectName("cleanupBox")
        self.gridLayout_2.addWidget(self.cleanupBox, 0, 0, 1, 1)
        self.logToFileBox = QtGui.QCheckBox(self.optionsBox)
        self.logToFileBox.setObjectName("logToFileBox")
        self.gridLayout_2.addWidget(self.logToFileBox, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.optionsBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(OptionsDialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(OptionsDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(OptionsDialog)
        QtCore.QMetaObject.connectSlotsByName(OptionsDialog)

    def retranslateUi(self, OptionsDialog):
        OptionsDialog.setWindowTitle(QtGui.QApplication.translate("OptionsDialog", "Open / Options", None, QtGui.QApplication.UnicodeUTF8))
        self.fileBox.setTitle(QtGui.QApplication.translate("OptionsDialog", "Files", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OptionsDialog", "Base translation:", None, QtGui.QApplication.UnicodeUTF8))
        self.openBaseButton.setText(QtGui.QApplication.translate("OptionsDialog", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("OptionsDialog", "Translated file:", None, QtGui.QApplication.UnicodeUTF8))
        self.openTransButton.setText(QtGui.QApplication.translate("OptionsDialog", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsBox.setTitle(QtGui.QApplication.translate("OptionsDialog", "Other options", None, QtGui.QApplication.UnicodeUTF8))
        self.cleanupBox.setText(QtGui.QApplication.translate("OptionsDialog", "Clean up translated file on save", None, QtGui.QApplication.UnicodeUTF8))
        self.logToFileBox.setText(QtGui.QApplication.translate("OptionsDialog", "Log console messagesto file", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("OptionsDialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("OptionsDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

