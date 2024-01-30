import sys

from PySide6 import QtWidgets

from src.ui.window import MainWindow

app = QtWidgets.QApplication(sys.argv)
app.setApplicationName("MusicMarkuppApp")
window = MainWindow()
window.show()
sys.exit(app.exec())
