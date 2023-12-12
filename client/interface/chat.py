## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.client import Client

from PyQt6.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QWidget, QSplitter, QScrollArea, QCheckBox, QPushButton, QGridLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import Qt, QSize

class ChatWindow(QMainWindow):
    def __init__(self, client:'Client'):
        super().__init__()
        self.client = client
        self.setWindowTitle("Chat server")
        self.setMinimumHeight(300)
        self.setMinimumWidth(500)
        self.resize(800, 600)

        self.splitter = QSplitter()

        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(100)
        self.list_widget.setMinimumWidth(100)
        self.splitter.addWidget(self.list_widget)

        self.add_room("home")

        for room in client.rooms:
            self.add_room(room)

        self.list_widget.itemClicked.connect(self.update_title)

        self.subwindow = QWidget()
        self.splitter.addWidget(self.subwindow)

        self.layout = QGridLayout()
        self.subwindow.setLayout(self.layout)

        self.setCentralWidget(self.splitter)

    def add_room(self, room):
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 100))

        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor("blue")))
        painter.drawEllipse(0, 0, 100, 100)
        painter.end()

        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText(room)

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, label)

    def update_title(self, item):
        label = self.list_widget.itemWidget(item)
        if label is not None:
            title = label.text()
            self.subwindow.setWindowTitle(title)

            # Clear the layout
            for i in reversed(range(self.layout.count())): 
                widget = self.layout.itemAt(i).widget()
                self.layout.removeWidget(widget)
                widget.setParent(None)

            if title == "HO":
                title = QLabel("Choose the rooms you want to join")
                self.layout.addWidget(title, 1, 1)

                for i, room in enumerate(self.client.all_rooms):
                    checkbox = QCheckBox(room)
                    self.layout.addWidget(checkbox, i + 2, 1)

                self.send_button = QPushButton("Send")
                self.layout.addWidget(self.send_button, len(self.client.all_rooms) + 2, 1)

                self.layout.setColumnStretch(0, 1)
                self.layout.setColumnStretch(2, 1)
                self.layout.setRowStretch(0, 1)
                self.layout.setRowStretch(len(self.client.all_rooms) + 3, 1)

            else:  # For other rooms
                # Add your widgets for other rooms here
                pass
        else:
            print("No widget set for item")
            