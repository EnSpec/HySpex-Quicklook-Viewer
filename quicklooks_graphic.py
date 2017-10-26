from PyQt5 import QtCore, QtGui, QtWidgets
import graphics_app_ui
import sys
import math

#UI Class taken from http://doc.qt.io/qt-5/qtwidgets-widgets-imageviewer-example.html
class QuickLookApp(QtWidgets.QMainWindow,graphics_app_ui.Ui_MainWindow):
    def __init__(self,parent = None):
        super(QuickLookApp,self).__init__(parent)
        self.setupUi(self)
        self.progressBar.setHidden(True)
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.total_rotation = 0
        self.loadFile('test.jpeg')
        self.key_event_dict = {
            ord('='):self.zoomIn,
            ord('-'):self.zoomOut,
            ord(','):lambda:self.rotateImage(-10),
            ord('.'):lambda:self.rotateImage(10),
            ord('0'):self.fitImageToView,
        }
        self.actionOpen.triggered.connect(self.askFile)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        #self.actionRotate.triggered.connect(self.rotateImageDialog)


    def askFile(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if(fname):
            self.loadFile(fname)

    def loadFile(self,fname):
        self.scene.clear()
        self.graphicsView.viewport().update()
        self.pixmap = QtGui.QPixmap(fname)
        self.graphics_pixmap_item = QtWidgets.QGraphicsPixmapItem(self.pixmap)
        self.scene.addPixmap(self.pixmap)

    def rotateImage(self,degrees=90):
        self.total_rotation += degrees
        self.graphicsView.rotate(degrees)

    def zoomIn(self):
        self.graphicsView.scale(1.1,1.1)

    def zoomOut(self):
        self.graphicsView.scale(1/1.1,1/1.1)

    def fitImageToView(self):
        pass

    def fullSizeImage(self):
        pass

    def keyPressEvent(self,e):
        if e.modifiers() == QtCore.Qt.ControlModifier: 
            if(e.key() in self.key_event_dict):
                self.key_event_dict[e.key()]()

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)

    viewer = QuickLookApp()
    viewer.show()
    
    sys.exit(app.exec_())
