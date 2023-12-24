import sys
from PyQt5 import QtWidgets
from src.components.Window import Window


app = QtWidgets.QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec_())
