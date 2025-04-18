from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from PyQt6.QtSvgWidgets import QSvgWidget
from guiHelper import QSpinBox, QPushButton, QTextWidget, QLabel, QSplitter
from helper import get_points_to_graph_from_file

class QScrollableImage(QScrollArea):

    class QImage(QSvgWidget):
        def __init__(self, clickable = False, stmtChangeFunc=None):
            QSvgWidget.__init__(self)

            self.mag = 1

            self.hi = None

            self.posDict = {}

            if clickable:
                self.mousePressEvent = self.getPos
                self.stmtChangeFunc = stmtChangeFunc

        def paintEvent(self, event):
            QSvgWidget.paintEvent(self, event)
            
            if self.hi:
                painter = QPainter(self)
                brush = QBrush(QColor(0, 0, 255, 50))
                painter.setBrush(brush)
                pen = QPen(Qt.GlobalColor.blue, 4)
                painter.setPen(pen)
                painter.scale(self.mag, self.mag)
                painter.drawRect(self.posDict[self.hi])
                painter.end()

        def getPos(self, event):
            x = round(event.pos().x()/self.mag)
            y = round(event.pos().y()/self.mag)
            
            for key, bb in self.posDict.items():
                if bb.contains(x,y):
                    if key != self.hi:
                        self.hi = key
                        self.repaint()
                        self.stmtChangeFunc(key)
                    return
            if self.hi is not None:
                self.hi = None
                self.repaint()

        def setMagnification(self, mag):
            self.mag = mag
            self.resize(self.initSize*mag)

        def setImage(self, imgPath:str|bytearray):
            self.renderer().load(imgPath)
            self.initSize = self.renderer().defaultSize()
            self.resize(self.initSize*self.mag)

        def setData(self, img:str, posDict:dict, hi:int|None):
            self.setImage(img)

            self.posDict.clear()

            self.hi = None

            img_height = self.initSize.height()

            for key, posDict in posDict.items():
                self.posDict[key] = QRect(posDict['x'], img_height-posDict['y']+1, posDict['w'], posDict['h'])

        def setHi(self, hi:int|None):
            self.hi = hi
            self.repaint()


    def __init__(self, clickable=False, stmtChangeFunc=None):
        QScrollArea.__init__(self)

        self.image = self.QImage(clickable, stmtChangeFunc)
        self.setWidget(self.image)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setScale(self, mag):
        # TODO
        # vRatio = 0.5
        # hRatio = 0.5

        # if self.verticalScrollBar().maximum() != 0:
        #     vRatio = self.verticalScrollBar().sliderPosition()/self.verticalScrollBar().maximum()
        # if self.horizontalScrollBar().maximum() != 0:
        #     hRatio = self.horizontalScrollBar().sliderPosition()/self.horizontalScrollBar().maximum()

        self.image.setMagnification(mag/100)

        # self.verticalScrollBar().setSliderPosition(round(vRatio*self.verticalScrollBar().maximum()))
        # self.horizontalScrollBar().setSliderPosition(round(hRatio*self.horizontalScrollBar().maximum()))
    
    def resetImage(self, img:str|bytearray):
        self.image.setImage(img)

    def resetData(self, img:str, posDict:dict, hi:int|None):
        self.image.setData(img, posDict, hi)
    
    def setHi(self, hi:int|None):
        self.image.setHi(hi)

class QCFGWindow(QWidget):
    def __init__(self, stmtChangeFunc, clickable=True):
        super(QWidget, self).__init__()

        self.imageViewer = QScrollableImage(clickable, stmtChangeFunc)

    
        self.zoomText = QLabel('Magnification:', self)
        self.zoomSpinBox = QSpinBox(self.imageViewer.setScale, 100, 50, 500, 10, self)
        self.zoomSpinBox.setSuffix('%')
        self.zoomSpinBox.setAccelerated(True)

        self.controls = QHBoxLayout()
        self.controls.addStretch()
        self.controls.addWidget(self.zoomText)
        self.controls.addWidget(self.zoomSpinBox)

        self.vBox = QVBoxLayout()
        self.vBox.addLayout(self.controls)
        self.vBox.addWidget(self.imageViewer)

        self.setLayout(self.vBox)

        self.vBox.setContentsMargins(0,0,0,0)

    def resetData(self, img:str, posDict:dict, hi:int|None=None):
        self.imageViewer.resetData(img, posDict, None)

    def setHighlight(self, hi:int|None):
        self.imageViewer.setHi(hi)

class QPTAWindow(QWidget):
    def __init__(self, infoText):
        super(QWidget, self).__init__()

        self.imageViewer = QScrollableImage()

        self.infoText = QLabel(infoText, self)
    
        self.zoomText = QLabel('Magnification:', self)
        self.zoomSpinBox = QSpinBox(self.imageViewer.setScale, 100, 50, 500, 10, self)
        self.zoomSpinBox.setSuffix('%')
        self.zoomSpinBox.setAccelerated(True)

        self.controls = QHBoxLayout()
        self.controls.addWidget(self.infoText)
        self.controls.addStretch()
        self.controls.addWidget(self.zoomText)
        self.controls.addWidget(self.zoomSpinBox)

        self.vBox = QVBoxLayout()
        self.vBox.addLayout(self.controls)
        self.vBox.addWidget(self.imageViewer)

        self.setLayout(self.vBox)

        self.vBox.setContentsMargins(0,0,0,0)

    def resetImage(self, jsonPath:str):
        self.imageViewer.resetImage(get_points_to_graph_from_file(jsonPath))

class QLFCPAWidget(QWidget):
    def __init__(self, parent:QWidget|None=None):
        QWidget.__init__(self, parent)

        self.LivenessFp = './results/lfcpa/la/iter_'
        self.PTAFp = './results/lfcpa/pta/iter_'

        self.currIter = -1
        self.currStmt = -1

        self.rounds = -1
        self.numLivenessIters = -1
        self.numPTAIters = -1

        self.PTAAnalysis = True

        self.PTAinNext = QPTAWindow("PTA in new")
        self.PTAoutNext = QPTAWindow("PTA out new")
        self.PTAResults = QSplitter(Qt.Orientation.Horizontal)
        self.PTAResults.addWidget(self.PTAinNext)
        self.PTAResults.addWidget(self.PTAoutNext)

        # New LA results
        self.LinNext = QTextWidget("Liveness in new")
        self.LoutNext = QTextWidget("Liveness out new")
        self.LResults = QSplitter(Qt.Orientation.Horizontal)
        self.LResults.addWidget(self.LinNext)
        self.LResults.addWidget(self.LoutNext)

        # Old results
        self.PTAinOld = QPTAWindow("PTA in old")
        self.PTAoutOld = QPTAWindow("PTA out old")
        PTAOld = QSplitter(Qt.Orientation.Horizontal)
        PTAOld.addWidget(self.PTAinOld)
        PTAOld.addWidget(self.PTAoutOld)

        self.LinOld = QTextWidget("Liveness in old")
        self.LoutOld = QTextWidget("Liveness out old")
        LOld = QSplitter(Qt.Orientation.Horizontal)
        LOld.addWidget(self.LinOld)
        LOld.addWidget(self.LoutOld)

        # Displayed Data
        self.dataSplitter = QSplitter(Qt.Orientation.Vertical)
        self.dataSplitter.addWidget(self.PTAResults)
        self.dataSplitter.addWidget(PTAOld)
        self.dataSplitter.addWidget(LOld)

        # Spin Boxes for selecting iter and round
        self.iterSpinBox = QSpinBox(self.changeIter, -1, -1, -1, parent=self)
        iterSpinBoxText = QLabel('Iteration:', self)

        self.roundSpinBox = QSpinBox(self.changeRound, -1, -1, -1, parent=self)
        roundSpinBoxText = QLabel('Round:', self)

        self.switchAnalysisButton = QPushButton('PTA', self.switchAnalysisType, self)

        iterControl = QHBoxLayout()
        iterControl.addWidget(iterSpinBoxText)
        iterControl.addWidget(self.iterSpinBox)
        iterControl.addSpacing(20)
        iterControl.addWidget(roundSpinBoxText)
        iterControl.addWidget(self.roundSpinBox)
        iterControl.addStretch()
        iterControl.addWidget(self.switchAnalysisButton)

        viewer = QVBoxLayout()
        viewer.addLayout(iterControl)
        viewer.addWidget(self.dataSplitter)

        self.setLayout(viewer)

        viewer.setContentsMargins(0,0,0,0)


    def getPath(self, iter:int, round:int, stmt:int):
        return str(iter)+'_'+str(round)+'stmt_'+str(stmt)

    def changeIter(self, newIter:int):
        self.roundSpinBox.resetValues(1, 1, self.rounds[newIter-1][1])
        self.currIter = newIter
        self.changeRound(1)

    def changeRound(self, newRound:int):
        if self.PTAAnalysis:
            self.PTAinNext.resetImage(self.PTAFp + self.getPath(self.currIter, newRound, self.currStmt) + '_in.json')
            self.PTAoutNext.resetImage(self.PTAFp + self.getPath(self.currIter, newRound, self.currStmt) + '_out.json')

            self.PTAinOld.resetImage(self.PTAFp + self.getPath(self.currIter, newRound-1, self.currStmt) + '_in.json')
            self.PTAoutOld.resetImage(self.PTAFp + self.getPath(self.currIter, newRound-1, self.currStmt) + '_out.json')

            self.LinOld.setText(self.LivenessFp + self.getPath(self.currIter, self.rounds[self.currIter-1][0], self.currStmt) + '_in.json')
            self.LoutOld.setText(self.LivenessFp + self.getPath(self.currIter, self.rounds[self.currIter-1][0], self.currStmt) + '_out.json')

        else:
            self.PTAinOld.resetImage(self.PTAFp + self.getPath(self.currIter, 0, self.currStmt) + '_in.json')
            self.PTAoutOld.resetImage(self.PTAFp + self.getPath(self.currIter, 0, self.currStmt) + '_out.json')

            self.LinNext.setText(self.LivenessFp + self.getPath(self.currIter, newRound, self.currStmt) + '_in.json')
            self.LoutNext.setText(self.LivenessFp + self.getPath(self.currIter, newRound, self.currStmt) + '_out.json')

            self.LinOld.setText(self.LivenessFp + self.getPath(self.currIter, newRound-1, self.currStmt) + '_in.json')
            self.LoutOld.setText(self.LivenessFp + self.getPath(self.currIter, newRound-1, self.currStmt) + '_out.json')

    def setData(self, iters):
        self.rounds = iters
        self.numLivenessIters = len(self.rounds)
        self.numPTAIters = self.numLivenessIters - (self.rounds[-1][1]==0)

        self.currIter = 1
        self.currStmt = 0

        self.PTAAnalysis = True
        self.switchAnalysisType()

        self.roundSpinBox.resetValues(1, 1, self.rounds[0][1])
        self.iterSpinBox.resetValues(1, 1, self.rounds[0][1])

        self.changeIter(1)

    def switchAnalysisType(self):
        self.PTAAnalysis = not self.PTAAnalysis

        if self.PTAAnalysis:
            if self.currIter>self.numPTAIters:
                self.PTAAnalysis = False
                return
            self.roundSpinBox.resetValues(1, 1, self.rounds[self.currIter-1][1])

            self.switchAnalysisButton.setText('PTA')
            self.dataSplitter.replaceWidget(0, self.PTAResults)
        else:
            self.roundSpinBox.resetValues(1, 1, self.rounds[self.currIter-1][0])
            self.switchAnalysisButton.setText('LA')
            self.dataSplitter.replaceWidget(0, self.LResults)

        self.roundSpinBox.setValue(1)
        self.changeRound(1)

    def setCurrStmt(self, stmt):
        self.currStmt = stmt
        self.changeRound(self.roundSpinBox.value())


if __name__ == '__main__':
    
    def run_test():
        
        from PyQt6.QtWidgets import QApplication
        
        import sys
       
        app = QApplication([])

        f = open('./position_dict.json', 'r')
        cnts = f.read()
        f.close()

        editor = QLFCPAWidget()
        
        editor.resize(255,790)
        editor.show()
    
        sys.exit(app.exec())

    
    run_test()