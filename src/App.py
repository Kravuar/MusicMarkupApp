import sys

from PyQt5 import QtWidgets

from src.components.widgets.multipage.MainWindow import MainWindow

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
