# from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QScrollArea
from PyQt6.QtWidgets import QPushButton as QPB, QWidget, QSpinBox as QSB, QPlainTextEdit as QPTE
import json

class QPushButton(QPB):
    def __init__(self, text:str, onClickFunc, parent:QWidget|None=None):
        QPB.__init__(self, text, parent)
        self.clicked.connect(onClickFunc)
        self.setFixedHeight(self.height())
        self.setFixedWidth(70)
        # print(self.minimumWidth())

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

class QText(QPTE):
    def __init__(self):
        QPTE.__init__(self)
        self.setDisabled(True)

    def setText(self, filePath:str):
        with open(filePath) as fp:
            # self.setPlainText(json.load(fp))
            dict = json.load(fp)
            if len(dict) == 0:
                self.setPlainText("NULL")
            else:
                self.setPlainText("\n".join(ptr+': '+(', '.join(flds)) for ptr, flds in dict.items()))