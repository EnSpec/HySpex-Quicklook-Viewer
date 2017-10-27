from PyQt5 import QtCore, QtGui, QtWidgets
import graphics_app_ui
from hyspex_parse import readlines_gdal
import sys
import os
import math

BANDS = [75,46,19]
class HyspexParseThread(QtCore.QThread):
    def __init__(self,parent,in_fname,out_fname):
        QtCore.QThread.__init__(self)
        self._in_fname = in_fname
        self._out_fname = out_fname
        #self._parent.progressBar.setRange(0,100)
        #self._parent.progressBar.setValue(0)
        #self._parent.progressBar.setHidden(False)
    def run(self):
        filled = 0
        data = readlines_gdal.readBIL(self._in_fname,BANDS,False)
        readlines_gdal.toGeoTiff(self._out_fname,data)

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
            ord('o'):self.askFile,
        }
        #menu items
        self.actionOpen.triggered.connect(self.askFile)
        self.actionZoomIn.triggered.connect(lambda:self.zoomIn(1.25))
        self.actionZoomOut.triggered.connect(lambda:self.zoomOut(1.25))
        #toolbar icons
        self.buttonZoomIn.clicked.connect(lambda:self.zoomIn(1.25))
        self.buttonZoomOut.clicked.connect(lambda:self.zoomOut(1.25))
        self.buttonRotateCCW.clicked.connect(lambda:self.rotateImage(-30))
        self.buttonRotateCW.clicked.connect(lambda:self.rotateImage(30))
        #self.actionRotate.triggered.connect(self.rotateImageDialog)



    def scrollEvent(self,event):
        if event.delta() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def askFile(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if(fname):
            name,ext = os.path.splitext(fname)
            #check for a hyspex file - it will need to be processed
            if ext in ['.hyspex','.bil']:
                out_fname = name+'.tiff'
                #check for a previously generated tiff file
                if not os.path.exists(out_fname):
                    #stick data processing in a thread so it doesn't hang the app
                    self.parseThread = HyspexParseThread(self,fname,out_fname)
                    self.parseThread.finished.connect(lambda:self.loadFile(out_fname))
                    self.parseThread.start()
                else:
                    self.loadFile(out_fname)
            else:
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

    def zoomIn(self,amt=1.1):
        self.graphicsView.scale(amt,amt)

    def zoomOut(self,amt=1.1):
        self.graphicsView.scale(1/amt,1/amt)

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
