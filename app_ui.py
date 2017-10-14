# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'app.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(817, 632)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName("scrollArea")
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setGeometry(QtCore.QRect(0, 0, 779, 553))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setText("")
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setObjectName("imageLabel")
        self.scrollArea.setWidget(self.imageLabel)
        self.verticalLayout.addWidget(self.scrollArea)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 817, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionOpen_Latest = QtWidgets.QAction(MainWindow)
        self.actionOpen_Latest.setObjectName("actionOpen_Latest")
        self.actionZoomIn = QtWidgets.QAction(MainWindow)
        self.actionZoomIn.setObjectName("actionZoomIn")
        self.actionZoomOut = QtWidgets.QAction(MainWindow)
        self.actionZoomOut.setObjectName("actionZoomOut")
        self.actionFitToView = QtWidgets.QAction(MainWindow)
        self.actionFitToView.setObjectName("actionFitToView")
        self.actionRotate = QtWidgets.QAction(MainWindow)
        self.actionRotate.setObjectName("actionRotate")
        self.actionFullSize = QtWidgets.QAction(MainWindow)
        self.actionFullSize.setObjectName("actionFullSize")
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionOpen_Latest)
        self.menuEdit.addAction(self.actionRotate)
        self.menuView.addAction(self.actionZoomIn)
        self.menuView.addAction(self.actionZoomOut)
        self.menuView.addAction(self.actionFitToView)
        self.menuView.addAction(self.actionFullSize)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionLoad.setText(_translate("MainWindow", "Open"))
        self.actionOpen_Latest.setText(_translate("MainWindow", "Open Latest"))
        self.actionZoomIn.setText(_translate("MainWindow", "Zoom In (Ctrl + +)"))
        self.actionZoomOut.setText(_translate("MainWindow", "Zoom Out (Ctrl + -)"))
        self.actionFitToView.setText(_translate("MainWindow", "Fit to Window (Ctrl + 0)"))
        self.actionRotate.setText(_translate("MainWindow", "Rotate (Ctrl + T)"))
        self.actionFullSize.setText(_translate("MainWindow", "Full Size"))

