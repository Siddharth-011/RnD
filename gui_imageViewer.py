from PyQt6.QtCore import Qt, QRect, QByteArray
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QSplitter
from PyQt6.QtGui import QColor, QFocusEvent, QPaintEvent, QPainter, QFont, QTextFormat, QTextCursor, QPen, QBrush
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer
from guiHelper import QSpinBox, QPushButton, QText
import json
from helper import get_points_to_graph_from_file


# class QScrollableImage(QScrollArea):

#     class QImage(QLabel):
#         def __init__(self, imgPath, posDict = None):
#             QLabel.__init__(self)

#             self.img = QPixmap(imgPath)

#             img_height = self.img.height()

#             if posDict is not None:
#                 self.posDict = {}
#                 self.hi = None

#                 for key, posDict in posDict.items():
#                     self.posDict[key] = QRect(posDict['x'], img_height-posDict['y']+1, posDict['w'], posDict['h'])

#                 self.mousePressEvent = self.getPos
#                 # print(self.posDict)

#             self.setPixmap(self.img)
#             self.setFixedSize(self.img.width(), self.img.height())

#         def getPos(self, event):
#             x = event.pos().x()
#             y = event.pos().y()
            
#             for key, bb in self.posDict.items():
#                 if bb.contains(x,y):
#                     if self.hi == key:
#                         return
#                     self.hi = key
#                     img = self.img.copy()
#                     painter = QPainter(img)
#                     brush = QBrush(QColor(0, 0, 255, 100))
#                     painter.setBrush(brush)
#                     pen = QPen(Qt.GlobalColor.blue, 5)
#                     painter.setPen(pen)
#                     painter.drawRect(bb)
#                     painter.end()
#                     self.setPixmap(img)
#                     print(key)
#                     return
#             if self.hi is not None:
#                 self.hi = None
#                 self.setPixmap(self.img)

#             self.setMagnification(1)

#         def setMagnification(self, mag):
#             # self.setPixmap(self.pixmap().scaled())
#             print(self.pixmap().size())
#             print(self.pixmap().size().scaled())

#     def __init__(self, imgPath, posDict = None):
#         QScrollArea.__init__(self)

#         # self.image = self.QImage(imgPath, posDict)
#         # self.setWidget(self.image)
#         self.image = QSvgWidget('./code.svg')
#         self.setWidget(self.image)
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class QScrollableImage(QScrollArea):

    class QImage(QSvgWidget):
        # def __init__(self, imgPath : str|bytearray, posDict : dict|None):
        def __init__(self, clickable = False, stmtChangeFunc=None):
            QSvgWidget.__init__(self)

            # self.renderer().load(imgPath)
            
            # self.initSize = self.renderer().defaultSize()
            # print(self.initSize)

            self.mag = 1

            self.hi = None

            self.posDict = {}

            if clickable:
                self.mousePressEvent = self.getPos
                self.stmtChangeFunc = stmtChangeFunc

            # if posDict is not None:
            #     img_height = self.initSize.height()

            #     for key, posDict in posDict.items():
            #         self.posDict[key] = QRect(posDict['x'], img_height-posDict['y']+1, posDict['w'], posDict['h'])

            #     self.mousePressEvent = self.getPos

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
            # print(x,y)
            
            for key, bb in self.posDict.items():
                if bb.contains(x,y):
                    if key != self.hi:
                        self.hi = key
                        self.repaint()
                        self.stmtChangeFunc(key)
                    # print(key)
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
            # self.hi = hi
            self.hi = None

            img_height = self.initSize.height()

            for key, posDict in posDict.items():
                self.posDict[key] = QRect(posDict['x'], img_height-posDict['y']+1, posDict['w'], posDict['h'])

        def setHi(self, hi:int|None):
            self.hi = hi
            self.repaint()


    # def __init__(self, imgPath, posDict = None):
    def __init__(self, clickable=False, stmtChangeFunc=None):
        QScrollArea.__init__(self)

        # self.image = self.QImage(imgPath, posDict)
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

    # def __init__(self, imgPath : str, posDict : dict):
    def __init__(self, stmtChangeFunc, clickable=True):
        super(QWidget, self).__init__()

        # self.imageViewer = QScrollableImage(imgPath, posDict)
        self.imageViewer = QScrollableImage(clickable, stmtChangeFunc)

    
        self.zoomText = QLabel('Magnification:', self)
        self.zoomSpinBox = QSpinBox(self.imageViewer.setScale, 100, 50, 500, 10, self)
        # self.zoomSpinBox.setMinimum(50)
        # self.zoomSpinBox.setMaximum(500)
        # self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setSuffix('%')
        self.zoomSpinBox.setAccelerated(True)

        # self.zoomSpinBox.valueChanged.connect(self.imageViewer.setScale)

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
    # def __init__(self, jsonPath : str):
    def __init__(self):
        super(QWidget, self).__init__()

        # self.imageViewer = QScrollableImage(get_points_to_graph_from_file(jsonPath))
        self.imageViewer = QScrollableImage()
    
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

    def resetImage(self, jsonPath:str):
        self.imageViewer.resetImage(get_points_to_graph_from_file(jsonPath))

class QLFCPAWidget(QWidget):
    # def __init__(self,resultsFilePath:str, parent:QWidget|None=None):
    def __init__(self, parent:QWidget|None=None):
        QWidget.__init__(self, parent)

        # self.fp = resultsFilePath
        # self.LivenessFp = resultsFilePath+'la/iter_'
        # self.PTAFp = resultsFilePath+'pta/iter_'
        self.LivenessFp = './results/lfcpa/la/iter_'
        self.PTAFp = './results/lfcpa/pta/iter_'

        # with open(resultsFilePath+'info.json') as f:
        #     infoDict = json.load(f)
        # self.rounds = infoDict['iters']
        # self.numLivenessIters = len(self.rounds)
        # self.numPTAIters = self.numLivenessIters - (self.rounds[-1][1]==0)

        self.currIter = -1
        self.currStmt = -1

        self.rounds = -1
        self.numLivenessIters = -1
        self.numPTAIters = -1

        self.PTAAnalysis = True

        # self.analysisTypeButton = QPushButton('Liveness', self.changeAnalysisTye, self)

        # self.PTAin = QPTAWindow(self.PTAFp + self.getPath(1, 1, 1) + '_in.json')
        # self.PTAout = QPTAWindow(self.PTAFp + self.getPath(1, 1, 1) + '_out.json')
        # New PTA data
        self.PTAinNext = QPTAWindow()
        self.PTAoutNext = QPTAWindow()
        PTAResults = QSplitter(Qt.Orientation.Horizontal)
        PTAResults.addWidget(self.PTAinNext)
        PTAResults.addWidget(self.PTAoutNext)

        self.newPTAWidget = QWidget()
        newPTA = QVBoxLayout(self.newPTAWidget)
        text = QLabel('Computed PTA results (in, out)')
        text.setFixedHeight(17)
        newPTA.addWidget(text)
        newPTA.addWidget(PTAResults)

        newPTA.setContentsMargins(0,0,0,0)

        # New LA results
        self.LinNext = QText()
        self.LoutNext = QText()
        LResults = QSplitter(Qt.Orientation.Horizontal)
        LResults.addWidget(self.LinNext)
        LResults.addWidget(self.LoutNext)

        self.newLAWidget = QWidget()
        newLA = QVBoxLayout(self.newLAWidget)
        text = QLabel('Computed LA results (in, out)')
        text.setFixedHeight(17)
        newLA.addWidget(text)
        newLA.addWidget(LResults)

        newLA.setContentsMargins(0,0,0,0)

        # Old results
        self.PTAinOld = QPTAWindow()
        self.PTAoutOld = QPTAWindow()
        PTAOld = QSplitter(Qt.Orientation.Horizontal)
        PTAOld.addWidget(self.PTAinOld)
        PTAOld.addWidget(self.PTAoutOld)

        self.LinOld = QText()
        self.LoutOld = QText()
        LOld = QSplitter(Qt.Orientation.Horizontal)
        LOld.addWidget(self.LinOld)
        LOld.addWidget(self.LoutOld)

        oldDataSplitter = QSplitter(Qt.Orientation.Vertical)
        oldDataSplitter.addWidget(PTAOld)
        oldDataSplitter.addWidget(LOld)
        oldDataSectionWidget = QWidget()
        oldDataSection = QVBoxLayout(oldDataSectionWidget)
        oldDataSection.addWidget(QLabel('Old results (in, out)'))
        oldDataSection.addWidget(oldDataSplitter)

        oldDataSection.setContentsMargins(0,0,0,0)

        # Displayed Data
        self.dataSplitter = QSplitter(Qt.Orientation.Vertical)
        self.dataSplitter.addWidget(self.newPTAWidget)
        self.dataSplitter.addWidget(oldDataSectionWidget)


        # Spin Boxes for selecting iter and round
        # self.iterSpinBox = QSpinBox(self.changeIter, 1, 1, self.numPTAIters, parent=self)
        self.iterSpinBox = QSpinBox(self.changeIter, -1, -1, -1, parent=self)
        iterSpinBoxText = QLabel('Iteration:', self)
        iterSpinBoxText.setFixedWidth(self.fontMetrics().horizontalAdvance('Iteration:'))

        # self.roundSpinBox = QSpinBox(self.changeRound, 1, 1, self.rounds[0][1], parent=self)
        self.roundSpinBox = QSpinBox(self.changeRound, -1, -1, -1, parent=self)
        roundSpinBoxText = QLabel('Round:', self)
        roundSpinBoxText.setFixedWidth(self.fontMetrics().horizontalAdvance('Round:'))

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
        # self.PTAin.resetImage(self.PTAFp + self.getPath(newIter, 1, 0) + '_in.json')
        # self.PTAout.resetImage(self.PTAFp + self.getPath(newIter, 1, 0) + '_out.json')
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
            self.dataSplitter.replaceWidget(0, self.newPTAWidget)
        else:
            self.roundSpinBox.resetValues(1, 1, self.rounds[self.currIter-1][0])
            self.switchAnalysisButton.setText('LA')
            self.dataSplitter.replaceWidget(0, self.newLAWidget)

        self.roundSpinBox.setValue(1)
        self.changeRound(1)

    def setCurrStmt(self, stmt):
        self.currStmt = stmt
        self.changeRound(self.roundSpinBox.value())


if __name__ == '__main__':
    
    def run_test():
        
        from PyQt6.QtWidgets import QApplication
        
        import sys
        # import json
       
        app = QApplication([])

        f = open('./position_dict.json', 'r')
        cnts = f.read()
        f.close()
        
        # editor = QCodeEditor()
        # w = QWidget()
        # editor = QHBoxLayout(w)
        # editor1 = QScrollableImage('./code.png', json.loads(cnts))
        # editor2 = QScrollableImage('./code.png', json.loads(cnts))

        # editor = QCFGWindow('./code.svg', json.loads(cnts))
        # editor = QPTAWindow('/home/siddharth/Desktop/RnD/git/RnD/results/lfcpa/pta/iter_2_2stmt_8_out.json')
        # editor = QLFCPAWidget('./results/lfcpa/')
        editor = QLFCPAWidget()
        # editor = QCFGWindow(None)
        # editor.addWidget(editor1)
        # editor.addWidget(editor2)
        editor.resize(255,790)
        editor.show()
    
        sys.exit(app.exec())

    
    run_test()