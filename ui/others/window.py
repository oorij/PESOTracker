from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont

class Window(QWidget):
    def __init__(self, parent=None, draggable=False, topbar=False):
        super().__init__(parent)
        self.draggable = draggable
        self.topbar_visible = topbar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.dragPos = None

        # Main wrapper
        self.wrapper = QWidget(self)
        self.wrapper.setObjectName("wrapper")
        self.wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.wrapper)

        # Top Bar (optional)
        self.top_bar = None
        if self.topbar_visible:
            self.top_bar = QWidget(self.wrapper)
            self.top_bar.setFixedHeight(35)
            self.top_bar.setObjectName("top_bar")
            top_bar_layout = QHBoxLayout()
            top_bar_layout.setContentsMargins(10, 0, 10, 0)
            self.top_bar.setLayout(top_bar_layout)
            self.setAttribute(Qt.WA_DeleteOnClose)

            # Title
            title = QLabel("PESO Database")
            title.setStyleSheet("color: white;")
            title.setFont(QFont("Segoe UI", 10))

            # Minimize button
            btn_min = QPushButton("-")
            btn_min.setFixedSize(30, 25)
            btn_min.setObjectName("btn_min")
            btn_min.clicked.connect(self.showMinimized)

            # Close button
            btn_close = QPushButton("X")
            btn_close.setFixedSize(30, 25)
            btn_close.setObjectName("btn_close")
            btn_close.clicked.connect(self.close)

            top_bar_layout.addWidget(title)
            top_bar_layout.addStretch()
            top_bar_layout.addWidget(btn_min)
            top_bar_layout.addWidget(btn_close)

            # Enable dragging events
            if self.draggable:
                self.top_bar.mousePressEvent = self._topbar_mouse_press
                self.top_bar.mouseMoveEvent = self._topbar_mouse_move

        # Main content layout
        self.content = QVBoxLayout()
        self.content.addStretch()

        # Layout for wrapper
        wrapper_layout = QVBoxLayout(self.wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        if self.topbar_visible:
            wrapper_layout.addWidget(self.top_bar)
        wrapper_layout.addLayout(self.content)
        wrapper_layout.setStretch(1, 1)

    # Internal topbar drag handlers
    def _topbar_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def _topbar_mouse_move(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos:
            self.move(event.globalPos() - self.dragPos)
            event.accept()