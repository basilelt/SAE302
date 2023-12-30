### Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.client import Client
    from PyQt6.QtGui import QCloseEvent

from PyQt6.QtWidgets import QMainWindow, QSplitter, QListWidget, QWidget, QGridLayout, QLabel, QCheckBox, QPushButton, QTextBrowser, QLineEdit, QListWidgetItem, QStackedLayout
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSlot

class ChatWindow(QMainWindow):
    """
    A QMainWindow subclass that represents the chat window of the application.

    :param client: The client that this window is associated with.
    :type client: Client
    """
    def __init__(self, client:'Client'):
        """
        Initialize the ChatWindow.

        :param client: The client that this window is associated with.
        :type client: Client
        """
        super().__init__()
        self.client = client
        self.setWindowTitle("Chat server")
        self.setMinimumHeight(300)
        self.setMinimumWidth(500)
        self.resize(800, 600)

        ## Create a splitter to manage layout of widgets
        self.splitter = QSplitter()

        ## Create a list widget to display rooms
        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(100)
        self.list_widget.setMinimumWidth(100)
        self.splitter.addWidget(self.list_widget)

        ## Initialize a dictionary to store messages
        self.messages = {}

        ## Add default rooms
        self.add_room("home")
        self.add_room("private")

        ## Add rooms from the client
        for room in client.rooms:
            self.add_room(room)

        ## Connect the itemClicked signal to the update_title slot
        self.list_widget.itemClicked.connect(self.update_title)

        ## Create a subwindow to display messages
        self.subwindow = QWidget()
        self.splitter.addWidget(self.subwindow)

        ## Create a stacked layout to manage the subwindow's layout
        self.stacked_layout = QStackedLayout()
        self.subwindow.setLayout(self.stacked_layout)

        ## Create widgets for home, private messages, and room
        self.home_widget = self.create_home_widget()
        self.private_message_widget = self.create_private_message_widget() 
        self.room_widget = self.create_room_widget()

        ## Add the widgets to the stacked layout
        self.stacked_layout.addWidget(self.home_widget)
        self.stacked_layout.addWidget(self.private_message_widget)
        self.stacked_layout.addWidget(self.room_widget)

        ## Set the central widget of the window to the splitter
        self.setCentralWidget(self.splitter)

    def add_room(self, room:str):
        """
        Add a room to the chat window.

        :param room: The name of the room to add.
        :type room: str
        """
        ## Create a new list widget item
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 100))

        ## Create a pixmap and fill it with a transparent color
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.transparent)

        ## Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor("blue")))
        painter.drawEllipse(0, 0, 100, 100)  ## Draw a blue circle
        painter.end()  ## End the painter's current painting path

        ## Create a label, set its pixmap, and center its text
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText(room)  ## Set the room name as the label's text

        ## Add the item and label to the list widget
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, label)

    def send_rooms(self):
        """
        Send the selected rooms to the server.
        """
        ## Initialize a list to store the selected rooms
        selected_rooms = []

        ## Iterate over all widgets in the home_widget's layout
        for i in range(self.home_widget.layout().count()):
            ## Get the widget at the current index
            widget = self.home_widget.layout().itemAt(i).widget()

            ## If the widget is a checkbox and it's checked, add its text (the room name) to the list
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_rooms.append(widget.text())

        ## For each selected room, send a pending room request to the server
        for room in selected_rooms:
            self.client.send_pending_room(room)
    
    def update_title(self, item:QListWidgetItem):
        """
        Update the title of the subwindow based on the selected item.

        :param item: The selected item.
        :type item: QListWidgetItem
        """
        ## Get the widget associated with the selected item
        label = self.list_widget.itemWidget(item)

        if label is not None:
            ## Get the room name from the label text
            title = label.text()

            ## Set the subwindow title to the room name
            self.subwindow.setWindowTitle(title)

            ## Depending on the room name, switch the current widget in the stacked layout
            if title == "home":
                self.stacked_layout.setCurrentWidget(self.home_widget)
            elif title == "private":
                self.stacked_layout.setCurrentWidget(self.private_message_widget)
                self.username_input.clear()  ## Clear the username input for private room
            else:
                self.stacked_layout.setCurrentWidget(self.room_widget)
                self.textBrowser.clear()  ## Clear the text browser for other rooms

                ## If there are messages for this room, append them to the text browser
                if title in self.messages:
                    for message in self.messages[title]:
                        self.textBrowser.append(message)
        else:
            print("No widget set for item")

    def create_home_widget(self) -> QWidget:
        """
        Create the home widget.

        :return: The created home widget.
        :rtype: QWidget
        """
        ## Create a new QWidget and a QGridLayout
        widget = QWidget()
        layout = QGridLayout()

        ## Set the layout of the widget
        widget.setLayout(layout)

        ## Create a QLabel with a title and add it to the layout
        title = QLabel("Choose the rooms you want to join")
        layout.addWidget(title, 1, 1)

        ## For each room, create a QCheckBox with the room name and add it to the layout
        for i, room in enumerate(self.client.all_rooms):
            checkbox = QCheckBox(room)
            layout.addWidget(checkbox, i + 2, 1)

        ## Create a QPushButton for sending the selected rooms and add it to the layout
        send_button = QPushButton("Send")
        layout.addWidget(send_button, len(self.client.all_rooms) + 2, 1)

        ## Set the column and row stretch factors to ensure the layout expands correctly
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(len(self.client.all_rooms) + 3, 1)

        ## Connect the button's clicked signal to the send_rooms method
        send_button.clicked.connect(self.send_rooms)

        ## Return the created widget
        return widget

    def create_private_message_widget(self) -> QWidget:
        """
        Create the private message widget.

        :return: The created private message widget.
        :rtype: QWidget
        """
        ## Create a new QWidget and a QGridLayout
        widget = QWidget()
        layout = QGridLayout()

        ## Set the layout of the widget
        widget.setLayout(layout)

        ## Create a QLabel with a title and add it to the layout
        title = QLabel("Send a private message")
        layout.addWidget(title, 1, 1)

        ## Create a QLabel for the username and add it to the layout
        username_label = QLabel("Username:")
        layout.addWidget(username_label, 2, 1)

        ## Create a QLineEdit for the username input and add it to the layout
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input, 2, 2)

        ## Create a QPushButton for sending the message and add it to the layout
        send_button = QPushButton("Send")
        layout.addWidget(send_button, 4, 1, 1, 2)

        ## Set the column and row stretch factors to ensure the layout expands correctly
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(5, 1)

        ## Connect the button's clicked signal to the send_private_message method
        send_button.clicked.connect(self.send_private_message)

        ## Return the created widget
        return widget

    def create_room_widget(self) -> QWidget:
        """
        Create the room widget.

        :return: The created room widget.
        :rtype: QWidget
        """
        ## Create a new QWidget and a QGridLayout
        widget = QWidget()
        layout = QGridLayout()

        ## Set the layout of the widget
        widget.setLayout(layout)

        ## Create a QTextBrowser for displaying messages and add it to the layout
        self.textBrowser = QTextBrowser()
        layout.addWidget(self.textBrowser, 1, 1, 1, 1) 

        ## Create a QLineEdit for inputting messages and add it to the layout
        self.messageInput = QLineEdit()
        layout.addWidget(self.messageInput, 2, 1)

        ## Create a QPushButton for sending the message and add it to the layout
        sendButton = QPushButton("Send")
        sendButton.clicked.connect(self.send_message)
        layout.addWidget(sendButton, 3, 1)

        ## Connect the public_message_received signal from the client to the display_public_message method
        self.client.public_message_received.connect(self.display_public_message)

        ## Return the created widget
        return widget

    def refresh_rooms(self):
        """
        Refresh the list of rooms.
        """
        ## Clear the list widget to remove all current items
        self.list_widget.clear()

        ## Add the "home" room to the list widget
        self.add_room("home")
        self.add_room("private")

        ## Iterate over all rooms in the client's room list
        for room in self.client.rooms:
            ## Add each room to the list widget
            self.add_room(room)
    
    @pyqtSlot()
    def send_message(self):
        """
        Send the message entered by the user to the server.
        """
        ## Get the text from the message input field
        message = self.messageInput.text()

        ## Get the title of the subwindow, which is the name of the current room
        room = self.subwindow.windowTitle()

        ## Use the client to send the message to the server, specifying the room and the message
        self.client.send_public_message(room, message)

        ## Clear the message input field
        self.messageInput.clear()
    
    @pyqtSlot()
    def send_private_message(self):
        """
        Send a private message to the specified user.
        """
        ## Get the text from the username input field
        username = self.username_input.text()

        ## If the username is not empty
        if username:
            ## Use the client to send a private message to the server, specifying the username and the message
            self.client.send_private_message(username, "initiate")

            ## Clear the username input field
            self.username_input.clear()
        else:
            ## If the username is empty, emit an error message
            self.client.error_received.emit("Invalid Input", "Username must be filled")

    @pyqtSlot(str, str, str)
    def display_public_message(self, room:str, sender:str, content:str):
        """
        Display a public message in the chat window.

        :param room: The room where the message was sent.
        :type room: str
        :param sender: The sender of the message.
        :type sender: str
        :param content: The content of the message.
        :type content: str
        """
        ## Format the message as "sender: content"
        message = f"{sender}: {content}"

        ## If the room is not already in the messages dictionary, add it with an empty list
        if room not in self.messages:
            self.messages[room] = []

        ## Append the message to the list of messages for the room
        self.messages[room].append(message)

        ## If the room is the same as the current room, append the message to the text browser
        if room == self.subwindow.windowTitle():
            self.textBrowser.append(message)

    def closeEvent(self, event:'QCloseEvent'):
        """
        Handle the close event of the window.

        :param event: The close event.
        :type event: QCloseEvent
        """
        ## Close the client connection and accept the event
        self.client.close()
        event.accept()
