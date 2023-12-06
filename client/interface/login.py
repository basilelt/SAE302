from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLineEdit, QLabel, QGridLayout, QFrame, QGroupBox, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set minimum width
        self.setMinimumWidth(600)
        
        widget = QWidget ()
        self.setCentralWidget(widget)
        
        grid = QGridLayout()
        widget.setLayout(grid)

        self.setWindowTitle("Login to a chat server")
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        # Get the window color of the current theme
        window_color = self.palette().color(QPalette.ColorRole.Window)
        # Darken the color by 20%
        darker_color = window_color.darker(120)
        # Get the text color of the current theme
        text_color = self.palette().color(QPalette.ColorRole.Text)
        # Set the background color, border style, corner radius, padding and button colors of the frame
        frame.setStyleSheet(f"""
            background-color: {darker_color.name()};
            border-style: solid;
            border-width: 1px;
            border-color: {darker_color.darker(150).name()};
            border-radius: 5px;
            padding: 10px;
            QLineEdit {{
                background-color: {darker_color.lighter(110).name()};
                border: none;
            }}
            QPushButton {{
                background-color: {text_color.name()};
                color: {window_color.name()};
                border-radius: 5px;
            }}
        """)
        frame.setMinimumWidth(400)
        frameLayout = QGridLayout(frame)

        # Create a group box for each pair of label and text field
        userGroup = QGroupBox()
        passwordGroup = QGroupBox()
        serverGroup = QGroupBox()
        portGroup = QGroupBox()

        user = QLabel("Username:")
        user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user.setStyleSheet("border: none")
        self.__user = QLineEdit()
        self.__user.setStyleSheet("border: none")

        password = QLabel("Password:")
        password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        password.setStyleSheet("border: none")
        self.__password = QLineEdit()
        self.__password.setStyleSheet("border: none")

        server = QLabel("Server address:")
        server.setAlignment(Qt.AlignmentFlag.AlignCenter)
        server.setStyleSheet("border: none")
        self.__server = QLineEdit()
        self.__server.setStyleSheet("border: none")
        
        port = QLabel("Server port:")
        port.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__port = QLineEdit()
        self.__port.setStyleSheet("border: none")
        connect = QPushButton("Connect")
        quit = QPushButton("Quit")
        register = QPushButton("Register")

        # Create a vertical layout for each group box
        userLayout = QVBoxLayout(userGroup)
        passwordLayout = QVBoxLayout(passwordGroup)
        serverLayout = QVBoxLayout(serverGroup)
        portLayout = QVBoxLayout(portGroup)

        # Add the label and text field to each group box
        userLayout.addWidget(user)
        userLayout.addWidget(self.__user)
        passwordLayout.addWidget(password)
        passwordLayout.addWidget(self.__password)
        serverLayout.addWidget(server)
        serverLayout.addWidget(self.__server)
        portLayout.addWidget(port)
        portLayout.addWidget(self.__port)

        # Add the group boxes to the frame layout
        frameLayout.addWidget(userGroup, 0, 0, 1, 2)
        frameLayout.addWidget(passwordGroup, 1, 0, 1, 2)
        frameLayout.addWidget(serverGroup, 2, 0, 1, 2)
        frameLayout.addWidget(portGroup, 3, 0, 1, 2)
        frameLayout.addWidget(connect, 4, 0, 1, 1)
        frameLayout.addWidget(quit, 4, 1, 1, 1)
        frameLayout.addWidget(register, 5, 0, 1, 2)

        # Add stretchable empty space on either side of the grid
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(2, 1)

        # Add stretchable empty space above and below the grid
        grid.setRowStretch(0, 1)
        grid.setRowStretch(2, 1)

        # Add the frame to the grid layout
        grid.addWidget(frame, 1, 1)