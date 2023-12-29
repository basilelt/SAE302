## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.client import Client

from PyQt6.QtWidgets import QMainWindow, QSplitter, QListWidget, QWidget, QGridLayout, QLabel, QCheckBox, QPushButton, QTextBrowser, QLineEdit, QListWidgetItem, QStackedLayout
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSlot

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

        self.messages = {}

        self.add_room("home")
        self.add_room("private")

        for room in client.rooms:
            self.add_room(room)

        self.list_widget.itemClicked.connect(self.update_title)

        self.subwindow = QWidget()
        self.splitter.addWidget(self.subwindow)

        self.stacked_layout = QStackedLayout()
        self.subwindow.setLayout(self.stacked_layout)

        self.home_widget = self.create_home_widget()
        self.private_message_widget = self.create_private_message_widget() 
        self.room_widget = self.create_room_widget()

        self.stacked_layout.addWidget(self.home_widget)
        self.stacked_layout.addWidget(self.private_message_widget)
        self.stacked_layout.addWidget(self.room_widget)

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

    def send_rooms(self):
        selected_rooms = []
        for i in range(self.home_widget.layout().count()):
            widget = self.home_widget.layout().itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_rooms.append(widget.text())
        for room in selected_rooms:
            self.client.send_pending_room(room)
    
    def update_title(self, item):
        label = self.list_widget.itemWidget(item)
        if label is not None:
            title = label.text()
            self.subwindow.setWindowTitle(title)

            if title == "home":
                self.stacked_layout.setCurrentWidget(self.home_widget)
            elif title == "private":
                self.stacked_layout.setCurrentWidget(self.private_message_widget)
                self.username_input.clear()
            else:
                self.stacked_layout.setCurrentWidget(self.room_widget)
                self.textBrowser.clear()
                if title in self.messages:
                    for message in self.messages[title]:
                        self.textBrowser.append(message)
        else:
            print("No widget set for item")

    def create_home_widget(self):
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)

        title = QLabel("Choose the rooms you want to join")
        layout.addWidget(title, 1, 1)

        for i, room in enumerate(self.client.all_rooms):
            checkbox = QCheckBox(room)
            layout.addWidget(checkbox, i + 2, 1)

        send_button = QPushButton("Send")
        layout.addWidget(send_button, len(self.client.all_rooms) + 2, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(len(self.client.all_rooms) + 3, 1)

        send_button.clicked.connect(self.send_rooms)

        return widget

    def create_private_message_widget(self):
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)

        title = QLabel("Send a private message")
        layout.addWidget(title, 1, 1)

        username_label = QLabel("Username:")
        layout.addWidget(username_label, 2, 1)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input, 2, 2)

        send_button = QPushButton("Send")
        layout.addWidget(send_button, 4, 1, 1, 2)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(5, 1)

        send_button.clicked.connect(self.send_private_message)

        return widget

    def create_room_widget(self):
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)

        self.textBrowser = QTextBrowser()
        layout.addWidget(self.textBrowser, 1, 1, 1, 1) 

        self.messageInput = QLineEdit()
        layout.addWidget(self.messageInput, 2, 1)

        sendButton = QPushButton("Send")
        sendButton.clicked.connect(self.send_message)
        layout.addWidget(sendButton, 3, 1)

        self.client.public_message_received.connect(self.display_public_message)

        return widget

    def refresh_rooms(self):
        self.list_widget.clear()
        self.add_room("home")
        for room in self.client.rooms:
            self.add_room(room)
    
    @pyqtSlot()
    def send_message(self):
        message = self.messageInput.text()
        room = self.subwindow.windowTitle()
        self.client.send_public_message(room, message)
        self.messageInput.clear()
    
    @pyqtSlot()
    def send_private_message(self):
        username = self.username_input.text()

        if username:
            self.client.send_private_message(username, "initiate")
            self.username_input.clear()
        else:
            self.client.error_received.emit("Invalid Input", "Username must be filled")

    @pyqtSlot(str, str, str)
    def display_public_message(self, room:str, sender:str, content:str):
        message = f"{sender}: {content}"
        if room not in self.messages:
            self.messages[room] = []
        self.messages[room].append(message)

        if room == self.subwindow.windowTitle():
            self.textBrowser.append(message)

    def closeEvent(self, event):
        """
        Overrides the closeEvent method to close the client.
        """
        self.client.close()
        event.accept()