import sys

from PyQt5 import QtWidgets

from src.ui.window import MainWindow

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
