# import dotenv
import sys

from PySide6 import QtWidgets

from src.ui.window import MainWindow


# dotenv.load_dotenv()
app = QtWidgets.QApplication(sys.argv)
app.setApplicationName("MusicMarkuppApp")
window = MainWindow()
window.show()
sys.exit(app.exec())

# from src.app.text_expansion import expand_text
# for chunk in expand_text("Очень энергичный, но начинается медленно, фортепиано играет повторяющуюся мелодию в высоких нотах. Затем струнная секция начинает играть очень энергичный мотив, подходя к середине тембр нарастает. Затем, присоединяется весь оркестр."):
#     print(chunk.choices[0].delta.content or "", end="")
