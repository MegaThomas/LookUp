# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
import requests, re
from lxml import html

class MainWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.search = ButtonLineEdit('./icon/search.png')
        self.search.buttonClicked.connect(self.on_search)
        self.search.editingFinished.connect(self.on_search)
        self.search.textChanged.connect(self.on_changed)
        # autocomplete
        self.completer = QtGui.QCompleter()
        self.search.setCompleter(self.completer)
        # definition
        self.defn = QtGui.QTextEdit(self)
        self.defn.setReadOnly(True)
        self.defn.setCurrentFont(QtGui.QFont('Arial', 14))
        self.defn.setFontPointSize(16)
        self.defn.setHtml('<p style="font-family: Arial; font-size: 16px;">Hello</p>')
        # layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.search, 1, 0)
        grid.addWidget(self.defn, 2, 0)
        self.setLayout(grid)
        # window settings
        self.setFont(QtGui.QFont('Arial', 14))
        self.setGeometry(100,100,300,400)
        self.setWindowTitle("FastFind")
        self.setWindowIcon(QtGui.QIcon("./icon/tick 2.png"))
        # session
        self.session = requests.Session()

    def on_changed(self, content):
        word = content.trimmed()
        url = 'https://www.vocabulary.com/dictionary/autocomplete?search='+word
        auto = self.session.get(url)
        option = html.fromstring(auto.content).xpath('//li/div/span[@class="word"]/text()')
        model = QtGui.QStringListModel()
        model.setStringList(option)
        self.completer.setModel(model)

    def on_search(self):
        word = self.search.text().trimmed()
        url = 'https://vocabulary.com/dictionary/definition.ajax?search='+word+'&lang=en'
        respond = self.session.get(url).content
        respond = re.search(r'<p\s*class\s*=\s*"short">.*</p>', respond).group()\
            +re.search(r'<p\s*class\s*=\s*"long">.*</p>', respond).group()
        respond = re.sub(r'(<p\s*class\s*=\s*"short")(>.*</p>)(<p\s*class\s*=\s*"long")(>.*</p>)',\
            r'\1 style="font-family: Arial; font-size: 16px;"\2\3 style="font-family: Arial; font-size: 16px;"\4', \
            respond)
        self.defn.setHtml(unicode(respond, 'utf-8'))

class ButtonLineEdit(QtGui.QLineEdit):
    buttonClicked = QtCore.pyqtSignal(bool)

    def __init__(self, icon_file, parent=None):
        super(ButtonLineEdit, self).__init__(parent)

        self.button = QtGui.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(icon_file))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(self.buttonClicked.emit)

        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 2))

    def resizeEvent(self, event):
        buttonSize = self.button.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frameWidth - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1)/2)
        super(ButtonLineEdit, self).resizeEvent(event)


def main():
    app = QtGui.QApplication(sys.argv)
    MW = MainWindow()
    MW.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()