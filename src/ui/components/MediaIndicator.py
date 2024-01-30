from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QStyle


class MediaIndicator(QWidget):
    class Status:
        GOOD = 'GOOD'
        CORRUPTED = 'CORRUPTED'
        UNSUPPORTED = 'UNSUPPORTED'
        LOADING = 'LOADING'

    _pixmap_map = {
        Status.GOOD: None,
        Status.CORRUPTED: QStyle.StandardPixmap.SP_MessageBoxCritical,
        Status.UNSUPPORTED: QStyle.StandardPixmap.SP_MessageBoxWarning,
        Status.LOADING: QStyle.StandardPixmap.SP_TitleBarContextHelpButton
    }

    _tooltip_map = {
        Status.GOOD: None,
        Status.UNSUPPORTED: "Provided media file isn't supported by the player.",
        Status.CORRUPTED: "Media file could not be resolved.",
        Status.LOADING: "Media is loading."
    }

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.icon_label = QLabel(self)
        self.layout.addWidget(self.icon_label)
        self.setLayout(self.layout)

    def set_status(self, status: Status):
        tooltip = self._tooltip_map[status]
        pixmap = self._pixmap_map[status]

        if pixmap:
            self.setVisible(True)
            self.icon_label.setPixmap(self.style().standardPixmap(pixmap))
        else:
            self.setVisible(False)
            self.icon_label.clear()

        self.icon_label.setToolTip(tooltip)
