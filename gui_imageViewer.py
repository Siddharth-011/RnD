from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QScrollArea
from PyQt6.QtGui import QColor, QFocusEvent, QPaintEvent, QPainter, QFont, QTextFormat, QTextCursor, QPixmap, QPen, QBrush
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer


class QScrollableImage(QScrollArea):

    class QImage(QLabel):
        def __init__(self, imgPath, posDict = None):
            QLabel.__init__(self)

            self.img = QPixmap(imgPath)

            img_height = self.img.height()

            if posDict is not None:
                self.posDict = {}
                self.hi = None

                for key, posDict in posDict.items():
                    self.posDict[key] = QRect(posDict['x'], img_height-posDict['y']+1, posDict['w'], posDict['h'])

                self.mousePressEvent = self.getPos
                # print(self.posDict)

            self.setPixmap(self.img)
            self.setFixedSize(self.img.width(), self.img.height())

        def getPos(self, event):
            x = event.pos().x()
            y = event.pos().y()
            
            for key, bb in self.posDict.items():
                if bb.contains(x,y):
                    if self.hi == key:
                        return
                    self.hi = key
                    img = self.img.copy()
                    painter = QPainter(img)
                    brush = QBrush(QColor(0, 0, 255, 100))
                    painter.setBrush(brush)
                    pen = QPen(Qt.GlobalColor.blue, 5)
                    painter.setPen(pen)
                    painter.drawRect(bb)
                    painter.end()
                    self.setPixmap(img)
                    print(key)
                    return
            if self.hi is not None:
                self.hi = None
                self.setPixmap(self.img)

            self.setMagnification(1)

        def setMagnification(self, mag):
            # self.setPixmap(self.pixmap().scaled())
            print(self.pixmap().size())
            print(self.pixmap().size().scaled())

    def __init__(self, imgPath, posDict = None):
        QScrollArea.__init__(self)

        # self.image = self.QImage(imgPath, posDict)
        # self.setWidget(self.image)
        self.image = QSvgWidget('./code.svg')
        self.setWidget(self.image)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class QScrollableImage2(QScrollArea):

    class QImage(QSvgWidget):
        def __init__(self, imgPath : str, posDict : dict|None):
            QSvgWidget.__init__(self)

            self.renderer().load(imgPath)
            self.initSize = self.renderer().defaultSize()
            # print(self.initSize)

            self.mag = 1

            self.hi = None

            if posDict is not None:
                self.posDict = {}
                img_height = self.initSize.height()

                for key, posDict in posDict.items():
                    self.posDict[key] = QRect(posDict['x'], img_height-posDict['y']+1, posDict['w'], posDict['h'])

                self.mousePressEvent = self.getPos

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
                    # print(key)
                    return
            if self.hi is not None:
                self.hi = None
                self.repaint()

        def setMagnification(self, mag):
            self.mag = mag
            self.resize(self.initSize*mag)

    def __init__(self, imgPath, posDict = None):
        QScrollArea.__init__(self)

        self.image = self.QImage(imgPath, posDict)
        self.setWidget(self.image)
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

class QImageWindow(QWidget):

    def __init__(self, imgPath : str, posDict : dict):
        super(QWidget, self).__init__()

        self.imageViewer = QScrollableImage2(imgPath, posDict)
    
        self.zoomText = QLabel('Magnification:', self)
        self.zoomSpinBox = QSpinBox(self)
        self.zoomSpinBox.setMinimum(50)
        self.zoomSpinBox.setMaximum(500)
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setSuffix('%')
        self.zoomSpinBox.setAccelerated(True)

        self.zoomSpinBox.valueChanged.connect(self.imageViewer.setScale)

        self.buttons = QHBoxLayout()
        self.buttons.addStretch()
        self.buttons.addWidget(self.zoomText)
        self.buttons.addWidget(self.zoomSpinBox)

        self.vBox = QVBoxLayout()
        self.vBox.addLayout(self.buttons)
        self.vBox.addWidget(self.imageViewer)

        self.setLayout(self.vBox)

if __name__ == '__main__':
    
    def run_test():
        
        from PyQt6.QtWidgets import QApplication
        
        import sys
        import json
       
        app = QApplication([])

        f = open('./position_dict.json', 'r')
        cnts = f.read()
        f.close()
        
        # editor = QCodeEditor()
        # w = QWidget()
        # editor = QHBoxLayout(w)
        # editor1 = QScrollableImage('./code.png', json.loads(cnts))
        # editor2 = QScrollableImage('./code.png', json.loads(cnts))

        editor = QImageWindow('./code.svg', json.loads(cnts))
        # editor.addWidget(editor1)
        # editor.addWidget(editor2)
        # editor.resize(400,250)
        editor.show()
    
        sys.exit(app.exec())

    
    run_test()