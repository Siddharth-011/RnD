from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import QWidget, QTextEdit, QPlainTextEdit, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QColor, QPainter, QFont, QTextFormat, QTextCursor
from guiHelper import QPushButton, QSpinBox, QLabel, QL
from main import perform_analysis

 
class QCodeEditor(QPlainTextEdit):
    class NumberBar(QWidget):
        '''class that deifnes textEditor numberBar'''

        def __init__(self, editor):
            QWidget.__init__(self, editor)
            
            self.editor = editor
            self.line_count = 1
            self.updateWidth(1)
            self.editor.blockCountChanged.connect(self.updateWidth)
            self.editor.updateRequest.connect(self.updateContents)
            self.font = QFont()
            self.numberBarColor = QColor("#e8e8e8")
            # self.hi_numberBarColor = QColor("#181818")
                     
        def paintEvent(self, event):
            
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.numberBarColor)
             
            block = self.editor.firstVisibleBlock()
 
            # Iterate over all visible text blocks in the document.
            while block.isValid():
                blockNumber = block.blockNumber()
                block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()

                # block_bot = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).bottom()
 
                # Check if the position of the block is out side of the visible area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break
 
                # We want the line number for the selected line to be bold.
                if blockNumber == self.editor.textCursor().blockNumber():
                    self.font.setBold(True)
                    painter.setPen(QColor("#000000"))
                    # bgColor = self.hi_numberBarColor
                else:
                    self.font.setBold(False)
                    painter.setPen(QColor("#717171"))
                    # bgColor = self.numberBarColor
                painter.setFont(self.font)
                
                # Draw the line number right justified at the position of the line.
                paint_rect = QRect(0, int(block_top), int(self.width())-5, int(self.editor.fontMetrics().height()))
                # paint_rect = QRect(0, int(block_top), int(self.width())-5, int(block_bot))
                # painter.fillRect(paint_rect, bgColor)
                painter.drawText(paint_rect, Qt.AlignmentFlag.AlignRight, str(blockNumber+1))
 
                block = block.next()
 
            painter.end()
            
            QWidget.paintEvent(self, event)
 
        def getWidth(self):
            width = self.fontMetrics().horizontalAdvance(str(self.line_count)) + 10
            return width      
        
        def updateWidth(self, line_count):
            self.line_count = line_count
            width = self.getWidth()
            
            if self.width() != width:
                self.setFixedWidth(width)
                self.editor.setViewportMargins(width, 0, 0, 0)

        def updateFont(self):
            self.updateWidth(self.line_count)
 
        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update(0, rect.y(), self.width(), rect.height())
            
            # if rect.contains(self.editor.viewport().rect()):   
            #     fontSize = self.editor.currentCharFormat().font().pointSize()
            #     self.font.setPointSize(fontSize)
            #     self.font.setStyle(QFont.Style.StyleNormal)
            #     self.updateWidth(self.line_count)
                
        
    def __init__(self, font = QFont("Ubuntu Mono", 11)):                        
        super(QCodeEditor, self).__init__()
        
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        self.numberBar = self.NumberBar(self)
            
        self.currentLineNumber = None
        self.blockHeight = None
        self.currentLineColor = self.palette().alternateBase()
        # self.currentLineColor = QColor("#e8e8e8")
        self.cursorPositionChanged.connect(self.highligtCurrentLine)

        # self.highligtCurrentLine()
                 
    def resizeEvent(self, *e):
        '''overload resizeEvent handler'''
                
        cr = self.contentsRect()
        rec = QRect(cr.left(), cr.top(), self.numberBar.getWidth(), cr.height())
        self.numberBar.setGeometry(rec)
        
        QPlainTextEdit.resizeEvent(self, *e)

    def focusInEvent(self, e):
        self.highligtCurrentLine()
        QPlainTextEdit.focusInEvent(self, e)
    
    def focusOutEvent(self, e):
        self.currentLineNumber = None
        self.setExtraSelections([])
        QPlainTextEdit.focusOutEvent(self, e)

    def highligtCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        newBlockHeight = self.blockBoundingRect(self.textCursor().block()).height()
        if newCurrentLineNumber != self.currentLineNumber or self.blockHeight != newBlockHeight:
            self.currentLineNumber = newCurrentLineNumber
            self.blockHeight = newBlockHeight

            temp_cursor = QTextCursor(self.textCursor().block())
            hi_selections = []
            hi_selection = QTextEdit.ExtraSelection() 
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)

            hi_selection.cursor = temp_cursor
            hi_selections.append(hi_selection)
            check = temp_cursor.movePosition(QTextCursor.MoveOperation.Down)

            while check and not temp_cursor.atBlockStart():
                hi_selection = QTextEdit.ExtraSelection(hi_selection) 
                hi_selection.cursor = temp_cursor
                hi_selections.append(hi_selection)
                check = temp_cursor.movePosition(QTextCursor.MoveOperation.Down)

            self.setExtraSelections(hi_selections)

    def updateFont(self, newFont):
        self.setFont(newFont)
        self.numberBar.updateFont()

class QCodeEditorWindow(QWidget):

    def __init__(self, parentAnalyzeFunc):
        super(QWidget, self).__init__()

        self.filePath = ''
        self.text = ''
        self.analyzedText = ''

        self.parentAnalyzeFunc = parentAnalyzeFunc

        initialFontSize = 20

        self.editorFont = QFont("Ubuntu Mono", initialFontSize)
        self.editor = QCodeEditor(self.editorFont)
        self.editor.textChanged.connect(self.updateAnalyzeSaveButtons)

        self.openButton = QPushButton('Open', self.openFile, self)
        self.saveButton = QPushButton('Save', self.saveFile, self)
        self.saveAsButton = QPushButton('SaveAs', self.saveAsFile, self)
        self.analyzeButton = QPushButton('Analyze', self.analyze, self)

        self.saveButton.setEnabled(False)

        self.zoomText = QLabel('Font:', self)
        self.zoomSpinBox = QSpinBox(self.updateFontSize, initialFontSize, 5, 150, parent=self)

        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.openButton)
        self.buttons.addWidget(self.saveButton)
        self.buttons.addWidget(self.saveAsButton)
        self.buttons.addWidget(self.analyzeButton)

        self.buttons.addStretch()

        self.buttons.addWidget(self.zoomText)
        self.buttons.addWidget(self.zoomSpinBox)

        self.errorMessage = QL()
        self.errorMessage.setStyleSheet("QLabel { background-color : lightgray; color : maroon; }")
        self.errorMessage.hide()

        self.vBox = QVBoxLayout()
        self.vBox.addLayout(self.buttons)
        self.vBox.addWidget(self.editor)

        self.setLayout(self.vBox)

        self.vBox.setContentsMargins(0,0,0,0)

    def openFile(self):
        newFilePath = QFileDialog.getOpenFileName(self, 'Open file')[0]

        if newFilePath and newFilePath != self.filePath:
            try:
                f = open(newFilePath, 'r')
                self.text = f.read()
                f.close()

                self.filePath = newFilePath
                self.editor.setPlainText(self.text)
                self.saveButton.setEnabled(False)
                print(self.filePath[self.filePath.rfind('/')+1:])
            except:
                print('Error in reading the file')

    def updateAnalyzeSaveButtons(self):
        if self.filePath:
            self.saveButton.setEnabled(self.text!=self.editor.toPlainText())

    def saveFile(self):
        try:
            editorText = self.editor.toPlainText()
            f = open(self.filePath, 'w')
            f.write(editorText)
            f.close()

            self.text = editorText
            self.saveButton.setEnabled(False)
        except:
            print('Error in saving the file')

    def saveAsFile(self):
        newFilePath = QFileDialog.getSaveFileName(self, 'Save as file')[0]
        if newFilePath:
            try:
                editorText = self.editor.toPlainText()
                f = open(newFilePath, 'w')
                f.write(editorText)
                f.close()

                self.filePath = newFilePath
                self.text = editorText
                self.saveButton.setEnabled(False)
            except:
                print('Error in saving the file')
    
    def updateFontSize(self, newFontSize):
        self.editorFont.setPointSize(newFontSize)
        self.editor.updateFont(self.editorFont)

    def analyze(self):
        err = perform_analysis(self.editor.toPlainText())
        self.vBox.removeWidget(self.errorMessage)
        if err:
            self.errorMessage.setText(err)
            self.vBox.addWidget(self.errorMessage)
            self.errorMessage.show()
        else:
            self.parentAnalyzeFunc()
            self.errorMessage.hide()

if __name__ == '__main__':

    def nop():
        pass
    
    def run_test():
        
        from PyQt6.QtWidgets import QApplication
        
        import sys
       
        app = QApplication([])
        
        editor = QCodeEditorWindow(nop)
        editor.resize(400,790)
        editor.show()
    
        sys.exit(app.exec())

    
    run_test()