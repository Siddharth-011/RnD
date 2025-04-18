from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton as QPB, QWidget, QSpinBox as QSB, QPlainTextEdit as QPTE, QLabel as QL, QHBoxLayout, QVBoxLayout, QSplitter as QS
from PyQt6.QtGui import QFont
import json

class QPushButton(QPB):
    def __init__(self, text:str, onClickFunc, parent:QWidget|None=None):
        QPB.__init__(self, text, parent)
        self.clicked.connect(onClickFunc)
        self.setFixedHeight(self.height())
        self.setFixedWidth(70)

class QSpinBox(QSB):
    def __init__(self, valChangeFunc, initialValue:int=50, minValue:int=0, maxValue:int=100, stepSize:int=1, parent:QWidget|None=None):
        QSB.__init__(self, parent)
        self.setMinimum(minValue)
        self.setMaximum(maxValue)
        self.setValue(initialValue)
        self.setSingleStep(stepSize)
        self.setFixedHeight(self.height())
        self.setFixedWidth(70)
        self.valueChanged.connect(valChangeFunc)

    def resetValues(self, initialValue:int=1, minValue:int=1, maxValue:int=100):
        self.setMinimum(minValue)
        self.setMaximum(maxValue)
        self.setValue(initialValue)

class QSplitter(QS):
    def __init__(self, parent = None):
        QS.__init__(self, parent)
        self.setHandleWidth(10)

class QLabel(QL):
    def __init__(self, text, parent=None):
        QL.__init__(self, text, parent)
        self.setFixedWidth(self.fontMetrics().horizontalAdvance(text))

class QTextWidget(QWidget):
    class QText(QPTE):
        def __init__(self, font):
            QPTE.__init__(self)
            self.setDisabled(True)
            self.setFont(font)

        def setText(self, filePath:str):
            with open(filePath) as fp:
                dict = json.load(fp)
                if len(dict) == 0:
                    self.setPlainText("NULL")
                else:
                    self.setPlainText("\n".join(ptr+': '+(', '.join(flds)) for ptr, flds in dict.items()))
        
        def updateFont(self, newFont):
            self.setFont(newFont)

    def __init__(self, infoText:str):
        QWidget.__init__(self)

        initialFontSize = 20

        self.editorFont = QFont("Ubuntu Mono", initialFontSize)
        self.editor = self.QText(self.editorFont)

        self.zoomText = QLabel('Font:', self)
        self.zoomText.setFixedWidth(self.fontMetrics().horizontalAdvance('Font:'))
        self.zoomSpinBox = QSpinBox(self.updateFontSize, initialFontSize, 5, 150, parent=self)

        self.infoText = QLabel(infoText)

        self.controls = QHBoxLayout()
        self.controls.addWidget(self.infoText)
        self.controls.addStretch()
        self.controls.addWidget(self.zoomText)
        self.controls.addWidget(self.zoomSpinBox)

        self.vBox = QVBoxLayout(self)
        self.vBox.addLayout(self.controls)
        self.vBox.addWidget(self.editor)
        self.vBox.setContentsMargins(0,0,0,0)

        self.setText = self.editor.setText

    def updateFontSize(self, newFontSize):
        self.editorFont.setPointSize(newFontSize)
        self.editor.updateFont(self.editorFont)