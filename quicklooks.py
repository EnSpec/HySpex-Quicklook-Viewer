from PyQt5 import QtCore, QtGui, QtWidgets
from multiprocessing import Process, Queue, Array
from datetime import datetime
import graphics_app_ui
import help_keys_ui
from hyspex_parse import readlines as readlines_gdal
import sys
import os
import math
from FileNavigator import FileNavigator

BANDS = {
    "VNIR":[75,46,19],
    "SWIR":[50,130,220]
}
DRIVE = 'R:\\'
def HyspexParser(tQ,rQ,arr):
    """Function for multiprocess that converts hyspex files to TIFFs,
    while providing updates on its current progress to its parent
    """
    while 1:
        task = tQ.get()
        #None is the poison pill
        if task is None:
            break
        #expects a 3-tuple of 2 strings and an int
        fname,out_fname,step = task
        wlens = "VNIR" if "VNIR" in fname else "SWIR"
        if wlens == "SWIR":
            step = max(int(step/3),1)
        try:
            data = readlines_gdal.readBIL(fname,BANDS[wlens],readmode='mmap',update_arr=arr,step=step)
            readlines_gdal.toGeoTiff(out_fname,data,wlens)
            rQ.put("OK")
        except RuntimeError:
            rQ.put("NOK")

class HelpDialog(QtWidgets.QDialog,help_keys_ui.Ui_Dialog):
    def __init__(self,parent=None):
        super(HelpDialog,self).__init__(parent)
        self.setupUi(self)

class QuickLookApp(QtWidgets.QMainWindow,graphics_app_ui.Ui_MainWindow):
    def __init__(self,parent = None):
        super(QuickLookApp,self).__init__(parent)
        self.setupUi(self)
        self.progressBar.setHidden(True)
        self.spinLabel.setHidden(True)
        self.cancelButton.setHidden(True)
        self.fileInfoWidget.setHidden(True)
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.total_rotation = 0
        self._old_fname = ''
        #keybindings
        self.key_event_dict = {
            ord('='):self.zoomIn,
            ord('-'):self.zoomOut,
            ord(','):lambda:self.rotateImage(-10),
            ord('.'):lambda:self.rotateImage(10),
            ord('['):lambda:self.changeLoadScale(1),
            ord(']'):lambda:self.changeLoadScale(-1),
            ord('H'):self.showHelp,
            ord('I'):self.showHelp,
            ord('O'):self.askFile,
            ord('L'):self.askLatest,
            ord('D'):self.focusDrive,
            ord('C'):self.cancelLoad,
            ord('V'):self.flipV,
            ord('B'):self.flipH,
        }
        #menu items
        self.actionOpen.triggered.connect(self.askFile)
        self.actionZoomIn.triggered.connect(lambda:self.zoomIn(1.25))
        self.actionZoomOut.triggered.connect(lambda:self.zoomOut(1.25))
        #toolbar icons
        self.aboutButton.clicked.connect(self.showHelp)
        self.buttonZoomIn.clicked.connect(lambda:self.zoomIn(1.25))
        self.buttonZoomOut.clicked.connect(lambda:self.zoomOut(1.25))
        self.buttonRotateCCW.clicked.connect(lambda:self.rotateImage(-30))
        self.buttonRotateCW.clicked.connect(lambda:self.rotateImage(30))
        self.buttonFlipH.clicked.connect(self.flipH)
        self.buttonFlipV.clicked.connect(self.flipV)
        #hyspex parser subprocess
        self.setupParser()
        #load spinner display
        self.spinGif = QtGui.QMovie("Assets/ajax-loader.gif")
        self.spinLabel.setMovie(self.spinGif)
        self.spinGif.start();
        #progress bar display
        self._fname = ''
        self.timer= QtCore.QTimer()
        self.timer.timeout.connect(self.getProgressUpdate)
        self.timer.start(1000)

        #image loading parameters
        self.loadscale = 4
        self.scaleUpButton.clicked.connect(lambda:self.changeLoadScale(-1))
        self.scaleDownButton.clicked.connect(lambda:self.changeLoadScale(1))
        self.changeLoadScale(0)
        self.pixmap=None
        #File Navigator for auto-detecting new files
        self.fn = FileNavigator(DRIVE)
        self.defaultDrive.addItems(self.fn._drives)
        self.defaultDrive.setCurrentIndex(self.fn._drives.index(self.fn._drive))
        self.defaultDrive.currentIndexChanged.connect(self.changeDrive);

        self.openButton.clicked.connect(self.askFile)
        self.loadLatestButton.clicked.connect(self.askLatest)
        self.cancelButton.clicked.connect(self.cancelLoad)


    def focusDrive(self):
        self.defaultDrive.showPopup()

    def setupParser(self):
        self.tQ = Queue()
        self.rQ = Queue()
        self.update_arr = Array('i',[0,0])
        self.parser = Process(target=HyspexParser,args=(self.tQ,self.rQ,self.update_arr),daemon=True)
        self.parser.start()
        self.parsing=False

    def changeLoadScale(self,dScale):
        self.loadscale +=dScale
        self.loadscale = min(max(self.loadscale,1),10)
        self.scaleLabel.setText("{}%".format(int(100/self.loadscale)))

    def cancelLoad(self):
        self.update_arr[1]=-1
        
        self.parsing=False
        self.progressBar.setHidden(True)
        self.cancelButton.setHidden(True)
        self.loadLatestButton.setEnabled(True)
        self.openButton.setEnabled(True)
        self.fileLabel.setText(self._old_fname)
        self._fname = self._old_fname

    def scrollEvent(self,event):
        if event.delta() > 0:
            self.zoomIn()
        else:
            self.zoomOut()


    def showHelp(self):
        help_dialog = HelpDialog(self)
        help_dialog.show()


    def changeDrive(self):
        self.fn.setDrive(self.defaultDrive.currentText())

    def askLatest(self):
        self.spinLabel.setHidden(False)
        self.fileInfoWidget.setHidden(False)
        self.fileLabel.setText("Searching drive {}".format(self.fn._drive))
        try:
            fname = self.fn.findLatest('.*VNIR.*hyspex$')
        except:
            self.fileLabel.setStyleSheet('color: red')
            self.fileLabel.setText("Error: No hyspex files found on drive {}".format(self.fn._drive))
        finally:
            self.spinLabel.setHidden(True)
        self.askFile(fname)

    def askFile(self,fname=None):
        if not fname:
            fname,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if(fname):
            name,ext = os.path.splitext(fname)
            #check for a hyspex file - it will need to be processed
            if ext in ['.hyspex','.bil','']:
                self.prepareLoad(fname,'tmp.png')
            else:
                self._fname = fname
                self.loadFile(fname)

    def prepareLoad(self,fname,out_fname):

        self._loaded = 0
        self._old_fname = self._fname
        self._fname = fname
        stats = os.stat(fname)
        size_gb = stats.st_size/1.e9
        self.sizeLabel.setText("%.2f GB"%size_gb)
        date = datetime.fromtimestamp(stats.st_ctime)
        self.dateLabel.setText(date.strftime("%Y-%m-%d"))
        self.timeLabel.setText(date.strftime("%H:%M:%S"))
        self.fileLabel.setStyleSheet('color: black')
        self.fileLabel.setText("Loading {}...".format(fname))
        self.update_arr[0]=0 
        self.update_arr[1]=0
        self.tQ.put((fname,out_fname,self.loadscale))
        self.fname = fname
        self.out_fname = out_fname
        self.result=0.
        self.value=0.
        self.parsing=True
        self.progressBar.setValue(0)
        self.loadLatestButton.setEnabled(False)
        self.openButton.setEnabled(False)
        self.progressBar.setHidden(False)
        self.cancelButton.setHidden(False)
        self.speedLabel.setHidden(False)
        self.speedLabel.setHidden(False)
        self.speedTextLabel.setHidden(False)

    def loadFile(self,fname):
        self.scene.clear()
        self.graphicsView.viewport().update()
        self.pixmap = QtGui.QPixmap(fname)
        self.graphics_pixmap_item = QtWidgets.QGraphicsPixmapItem(self.pixmap)
        self.scene.addPixmap(self.pixmap)
        self.fileLabel.setText(self._fname)
        self.graphicsView.setFocus()

    def flipH(self):
        if self.pixmap:
            self.scene.clear()
            self.pixmap = self.pixmap.transformed(QtGui.QTransform().scale(1, -1))
            self.graphics_pixmap_item = QtWidgets.QGraphicsPixmapItem(self.pixmap)
            self.scene.addPixmap(self.pixmap)

    def flipV(self):
        if self.pixmap:
            self.scene.clear()
            self.pixmap = self.pixmap.transformed(QtGui.QTransform().scale(-1, 1))
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
            if(self.update_arr[1]):
                self.progressBar.setValue(int(100*float(self.update_arr[0])/self.update_arr[1]))
                self.linesLabel.setText(str(self.update_arr[1]))
                self.speedLabel.setText(str((self.update_arr[0]-self._loaded))+"Ln/s")
                self._loaded = self.update_arr[0]

            #check for result from parser
            if not self.rQ.empty():
                self.result = self.rQ.get()

                if self.result == "OK":
                    #file is fully parsed and ready to go
                    self.parsing=False
                    self.loadFile(self.out_fname)
                    self.progressBar.setHidden(True)
                    self.cancelButton.setHidden(True)
                    self.speedLabel.setHidden(True)
                    self.speedTextLabel.setHidden(True)
                    self.loadLatestButton.setEnabled(True)
                    self.openButton.setEnabled(True)
                    self.speedLabel.setText("")
                if self.result == "NOK":
                    pass

        
    def cleanup(self):
        self.tQ.put(None)
        self.parser.join()
    
def run():
    app = QtWidgets.QApplication(sys.argv)

    viewer = QuickLookApp()
    viewer.show()
    app.exec_()
    viewer.cleanup()

if __name__ == '__main__':
    run()
