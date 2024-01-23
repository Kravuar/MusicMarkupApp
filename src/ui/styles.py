from pathlib import Path

from PySide6 import QtGui
from PySide6.QtGui import QColor


class GlobalStyle:
    _icon_path = Path("assets/icon.png")
    _white = QColor('#ffffff')
    _gray_lightest = QColor('#f8f7f8')
    _gray_lighter = QColor('#e5e4e4')
    _gray_light = QColor('#d1d0d1')
    _gray = QColor('#bebdbe')
    _gray_dark = QColor('#969696')
    _gray_darker = QColor('#6f6e6f')
    _gray_darkest = QColor('#484848')
    _black = QColor('#212021')

    _brand_light = QColor('#d5bfd2')
    _brand = QColor('#550055')
    _brand_dark = QColor('#2d0c2c')

    _cta_light = QColor('#c8d2bc')
    _cta = QColor('#2b5500')
    _cta_dark = QColor('#1b2c08')

    _info_light = QColor('#daecf6')
    _info = QColor('#58b3db')
    _info_dark = QColor('#315667')

    _warning_light = QColor('#fcebce')
    _warning = QColor('#dfb136')
    _warning_dark = QColor('#6a5521')

    _success_light = QColor('#d9f0d3')
    _success = QColor('#5bc150')
    _success_dark = QColor('#325c2b')

    _danger_light = QColor('#ffcfce')
    _danger = QColor('#dd2749')
    _danger_dark = QColor('#6a1f27')

    @staticmethod
    def create_stylesheet():
        stylesheet = f"""
            * {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 24px;
                color: {GlobalStyle._gray_darkest.name()};
            }}
            
            QMainWindow {{
                background: {GlobalStyle._gray_lightest.name()};
            }}
            
            QWidget {{
                color: {GlobalStyle._black.name()};
            }}
            
            QAbstractButton {{
                background: {GlobalStyle._brand_light.name()};
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: {GlobalStyle._white.name()};
            }}
            
            QAbstractButton:hover {{
                background: {GlobalStyle._brand.name()};
            }}
            
            QAbstractButton:pressed {{
                background: {GlobalStyle._brand_dark.name()};
            }}
            
            QLineEdit, QTextEdit {{
                padding: 6px;
            }}
            
            QLineEdit, QTextEdit {{
                background: {GlobalStyle._white.name()};
                border-radius: 5px;
                border: 1px solid {GlobalStyle._brand_light.name()};
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {GlobalStyle._brand.name()};
            }}
            
            QScrollArea {{
                background: none;
            }}
            
            QTabWidget::pane {{
                background: {GlobalStyle._gray_lightest.name()};
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                border: 1px solid {GlobalStyle._gray.name()};
            }}
            
            QTabBar::tab {{
                background: {GlobalStyle._gray_lighter.name()};
                padding: 10px;
                border: 1px solid {GlobalStyle._gray_light.name()};
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            
            QTabBar::tab:hover {{
                background: {GlobalStyle._gray.name()};
            }}
            
            QTabBar::tab:selected {{
                background: {GlobalStyle._white.name()};
                border-color: {GlobalStyle._brand.name()};
            }}
            
            QPushButton {{
                background: {GlobalStyle._cta.name()};
                color: {GlobalStyle._white.name()};
            }}
            
            QPushButton:disabled {{
                background: {GlobalStyle._gray.name()};
                color: {GlobalStyle._gray_light.name()};
            }}
            
            QLabel {{
                color: {GlobalStyle._gray_darkest.name()};
                background: {GlobalStyle._gray_lighter.name()};
                border: 3px solid {GlobalStyle._brand.name()};
                border-top: none;
                border-bottom: none;
                border-right: none;
            }}
            
            QMessageBox QLabel {{
                background: none;
                border: none;
            }}
        """

        return stylesheet

    @staticmethod
    def get_icon():
        return QtGui.QIcon(str(GlobalStyle._icon_path.resolve()))
