from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QApplication
from guiHelper import QSplitter
from gui_imageViewer import QLFCPAWidget, QCFGWindow
from gui_editor import QCodeEditorWindow
import sys
import json

class QApp(QWidget):
    def __init__(self, parent: QWidget | None=None):
        QWidget.__init__(self, parent)

        self.editor = QCodeEditorWindow(self.analyzeFunc)
        self.results = QLFCPAWidget()
        self.cfgWindow = QCFGWindow(self.results.setCurrStmt)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.cfgWindow)
        splitter.addWidget(self.results)

        hbox = QHBoxLayout(self)
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def changeAnalysisType(self, type:str):
        with open('./results/'+type+'/info.json') as f:
            infoDict = json.load(f)
        self.cfgWindow.resetData('./results/'+type+'/code.svg', infoDict['pos_dicts'])
        self.results.setData(infoDict['iters'])

    def analyzeFunc(self):
        self.changeAnalysisType('lfcpa')


if __name__ == '__main__':
    app = QApplication([])
    window = QWidget()

    window = QApp()
    window.setWindowTitle('PTA-Viz')
    window.resize(1800, 900)

    window.show()
    sys.exit(app.exec())