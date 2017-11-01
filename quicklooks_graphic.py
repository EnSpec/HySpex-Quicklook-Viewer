from PyQt5 import QtCore, QtGui, QtWidgets
from multiprocessing import Process, Queue
import graphics_app_ui
from hyspex_parse import readlines_gdal
import sys
import os
import math

BANDS = [75,46,19]
def HyspexParser(tQ,rQ):
    """Function for multiprocess that converts hyspex files to TIFFs,
    while providing updates on its current progress to its parent
    """
    while 1:
        #expects a 2-tuple of strings
        fname,out_fname=tQ.get()
        #None is the poison pill
        if fname is None:
            break
        print("Parsing {} to {}".format(fname,out_fname))
        filled = 33
        for data in readlines_gdal.readBIL(fname,BANDS):
            print(data)
            if data is None:
                rQ.put(filled)
                filled+=33

        readlines_gdal.toGeoTiff(out_fname,data)
        rQ.put("OK")

class QuickLookApp(QtWidgets.QMainWindow,graphics_app_ui.Ui_MainWindow):
    def __init__(self,parent = None):
        super(QuickLookApp,self).__init__(parent)
        self.setupUi(self)
        self.progressBar.setHidden(True)
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.total_rotation = 0
        self.key_event_dict = {
            ord('='):self.zoomIn,
            ord('-'):self.zoomOut,
            ord(','):lambda:self.rotateImage(-10),
            ord('.'):lambda:self.rotateImage(10),
            ord('O'):self.askFile,
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
        #hyspex parser subprocess
        self.tQ = Queue()
        self.rQ = Queue()
        self.parser = Process(target=HyspexParser,args=(self.tQ,self.rQ))
        self.parser.start()
        self.parsing=False
        #progress bar display
        self.timer= QtCore.QTimer()
        self.timer.timeout.connect(self.getProgressUpdate)
        self.timer.start(1000)

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
            if ext in ['.hyspex','.bil','']:
                out_fname = name+'.tiff'
                #check for a previously generated tiff file
                if not os.path.exists(out_fname):
                    #offload data processing to a subprocess so so it doesn't hang the app
                    self.prepareLoad(fname,out_fname)
                else:
                    self.loadFile(out_fname)
            else:
                self.loadFile(fname)

    def prepareLoad(self,fname,out_fname):
        #estimate the load time for the file
        #Tests show it's about 20 seconds per GB per band
        fsize = os.path.getsize(fname)
        load_time = 2 * 20 * (fsize/1e9) 
        self.load_rate = 100./load_time
        self.tQ.put((fname,out_fname))
        self.fname = fname
        self.out_fname = out_fname
        self.result=0.
        self.value=0.
        self.parsing=True
        self.progressBar.setValue(0)
        self.progressBar.setHidden(False)

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

    def keyPressEvent(self,e):
        if e.modifiers() == QtCore.Qt.ControlModifier: 
            if(e.key() in self.key_event_dict):
                self.key_event_dict[e.key()]()


    def getProgressUpdate(self):
        if not self.parsing:
            return
        else:
            #get every result from the parser
            while not self.rQ.empty():
                self.result = self.rQ.get()
                print("got",self.result)

            if self.result == "OK":
                #file is fully parsed and ready to go
                self.parsing=False
                self.loadFile(self.out_fname)
                self.progressBar.setHidden(True)
            else:
                self.value+=self.load_rate
                if(self.value < self.result):
                    self.value = self.result
                elif (self.value > self.result+66):
                    self.value = self.result+66
                self.progressBar.setValue(int(self.value))


        
    def cleanup(self):
        self.tQ.put((None,None))
        self.parser.join()
    

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)

    viewer = QuickLookApp()
    viewer.show()
    app.exec_()
    viewer.cleanup()

