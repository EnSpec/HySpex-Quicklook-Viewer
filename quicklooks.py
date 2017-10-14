from PyQt5 import QtCore, QtGui, QtWidgets
import app_ui
import rotate_form_ui
import sys
import math

class RotateDialog(QtWidgets.QDialog,rotate_form_ui.Ui_Dialog):
    def __init__(self,parent=None):
        super(RotateDialog,self).__init__(parent)
        self.setupUi(self)

    def getRotation(self,parent=None):
        dialog = RotateDialog(parent=parent)
        result = self.exec_()
        return int(self.rotationInput.text())


#UI Class taken from http://doc.qt.io/qt-5/qtwidgets-widgets-imageviewer-example.html
class QuickLookApp(QtWidgets.QMainWindow,app_ui.Ui_MainWindow):
    def __init__(self,parent = None):
        super(QuickLookApp,self).__init__(parent)
        self.setupUi(self)
        self.loadFile('test.jpeg')

        self.actionFitToView.triggered.connect(self.fitImageToView)
        self.actionFullSize.triggered.connect(self.fullSizeImage)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionRotate.triggered.connect(self.rotateImage)


    def loadFile(self,fname):
        self.pixmap = QtGui.QPixmap(fname)
        self.pixmap_size = self.pixmap.size()
        self.curr_pixmap = self.pixmap
        self.total_rotation = 0
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.resize(self.pixmap.size())

    def rotateImage(self):
        dialog = RotateDialog()
        self.total_rotation = dialog.getRotation()
        rotate = QtGui.QTransform().rotate(self.total_rotation)
        self.curr_pixmap = self.pixmap.transformed(rotate)
        self.imageLabel.setPixmap(self.curr_pixmap)
        self.imageLabel.resize(self.curr_pixmap.size())
        self.fitImageToView()

    def zoomIn(self):
        currSize = self.imageLabel.size()
        self.imageLabel.resize(currSize.width()*1.25,currSize.height()*1.25)
    def zoomOut(self):
        currSize = self.imageLabel.size()
        self.imageLabel.resize(currSize.width()*0.8,currSize.height()*0.8)

    def fitImageToView(self):
        self.imageLabel.resize(self.scrollArea.size())

    def fullSizeImage(self):
        self.imageLabel.resize(self.curr_pixmap.size())
        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)

    viewer = QuickLookApp()
    viewer.show()
    
    sys.exit(app.exec_())
