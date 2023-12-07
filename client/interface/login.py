from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLineEdit, QLabel, QGridLayout, QFrame, QGroupBox, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QSize, QSequentialAnimationGroup, QTimer
from PyQt6.QtGui import QPalette, QColor

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.animationGroup = None
        self.setMinimumWidth(600)
        widget = QWidget ()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)
        self.setWindowTitle("Login to a chat server")
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        window_color = self.palette().color(QPalette.ColorRole.Window)
        darker_color = window_color.darker(120)
        text_color = self.palette().color(QPalette.ColorRole.Text)
        
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
        
        userGroup = QGroupBox()
        passwordGroup = QGroupBox()
        serverGroup = QGroupBox()
        portGroup = QGroupBox()

        user = QLabel("Username:")
        user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user.setStyleSheet("border: none")
        self.__user = QLineEdit()
        self.__user.setStyleSheet(f"background-color: {darker_color.darker(110).name()}; border: none")

        password = QLabel("Password:")
        password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        password.setStyleSheet("border: none")
        self.__password = QLineEdit()
        self.__password.setStyleSheet(f"background-color: {darker_color.darker(110).name()}; border: none")

        server = QLabel("Server address:")
        server.setAlignment(Qt.AlignmentFlag.AlignCenter)
        server.setStyleSheet("border: none")
        self.__server = QLineEdit()
        self.__server.setStyleSheet(f"background-color: {darker_color.darker(110).name()}; border: none")
        
        port = QLabel("Server port:")
        port.setAlignment(Qt.AlignmentFlag.AlignCenter)
        port.setStyleSheet("border: none")
        self.__port = QLineEdit()
        self.__port.setStyleSheet(f"background-color: {darker_color.darker(110).name()}; border: none")

        self.connect = QPushButton("Connect")
        self.quit = QPushButton("Quit")
        self.register = QPushButton("Register")

        self.connectOriginalSize = self.connect.size()
        self.quitOriginalSize = self.quit.size()
        self.registerOriginalSize = self.register.size()

        self.connectAnimation = QPropertyAnimation(self.connect, b"geometry")
        self.quitAnimation = QPropertyAnimation(self.quit, b"geometry")
        self.registerAnimation = QPropertyAnimation(self.register, b"geometry")

        self.connect.clicked.connect(lambda: self.animateButton(self.connect, self.connectAnimation, self.connectOriginalSize))
        self.quit.clicked.connect(lambda: self.animateButton(self.quit, self.quitAnimation, self.quitOriginalSize))
        self.register.clicked.connect(lambda: self.animateButton(self.register, self.registerAnimation, self.registerOriginalSize))
        
        userLayout = QVBoxLayout(userGroup)
        passwordLayout = QVBoxLayout(passwordGroup)
        serverLayout = QVBoxLayout(serverGroup)
        portLayout = QVBoxLayout(portGroup)
        
        userLayout.addWidget(user)
        userLayout.addWidget(self.__user)
        passwordLayout.addWidget(password)
        passwordLayout.addWidget(self.__password)
        serverLayout.addWidget(server)
        serverLayout.addWidget(self.__server)
        portLayout.addWidget(port)
        portLayout.addWidget(self.__port)

        frameLayout.addWidget(userGroup, 0, 0, 1, 2)
        frameLayout.addWidget(passwordGroup, 1, 0, 1, 2)
        frameLayout.addWidget(serverGroup, 2, 0, 1, 2)
        frameLayout.addWidget(portGroup, 3, 0, 1, 2)
        frameLayout.addWidget(self.connect, 4, 0, 1, 1)
        frameLayout.addWidget(self.quit, 4, 1, 1, 1)
        frameLayout.addWidget(self.register, 5, 0, 1, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(2, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(2, 1)

        grid.addWidget(frame, 1, 1)

    def showEvent(self, event):
        self.connectOriginalSize = self.connect.size()
        self.quitOriginalSize = self.quit.size()
        self.registerOriginalSize = self.register.size()

        self.connect.clicked.connect(lambda: self.animateButton(self.connect, self.connectAnimation, self.connectOriginalSize))
        self.quit.clicked.connect(lambda: self.animateButton(self.quit, self.quitAnimation, self.quitOriginalSize))
        self.register.clicked.connect(lambda: self.animateButton(self.register, self.registerAnimation, self.registerOriginalSize))


    def animateButton(self, button, animation, originalSize):
        # Check if the animation is still running
        if animation.state() == QPropertyAnimation.State.Running:
            # Stop the current animation
            animation.stop()

        # Create a shadow effect
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 255))
        shadow.setOffset(0)

        # Apply the shadow effect to the button
        button.setGraphicsEffect(shadow)

        # Create an animation for the blur radius
        blurAnimation = QPropertyAnimation(shadow, b"blurRadius")

        # Set the animation parameters
        blurAnimation.setStartValue(10)
        blurAnimation.setEndValue(0)
        blurAnimation.setDuration(100)

        # Create an animation for the shadow color
        colorAnimation = QPropertyAnimation(shadow, b"color")

        # Set the animation parameters
        colorAnimation.setStartValue(QColor(0, 0, 0, 255))
        colorAnimation.setEndValue(QColor(0, 0, 0, 0))
        colorAnimation.setDuration(1000)

        # Create the size animation
        sizeAnimation = QPropertyAnimation(button, b"size")
        sizeAnimation.setStartValue(originalSize)
        sizeAnimation.setEndValue(originalSize - QSize(10, 10))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEndValue(originalSize)

        # Create a sequential animation group
        self.animationGroup = QSequentialAnimationGroup()

        # Add the animations to the group
        self.animationGroup.addAnimation(sizeAnimation)
        self.animationGroup.addAnimation(blurAnimation)
        self.animationGroup.addAnimation(colorAnimation)

        # Start the animation group
        self.animationGroup.start()

        # Remove the shadow effect when the animation ends
        self.animationGroup.finished.connect(lambda: button.setGraphicsEffect(None))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.__user.hasFocus():
                self.__password.setFocus()
            elif self.__password.hasFocus():
                self.__server.setFocus()
            elif self.__server.hasFocus():
                self.__port.setFocus()
            elif self.__port.hasFocus():
                self.connect.click()
                
    def onConnectClicked(self):
        pass

    def onQuitClicked(self):
        pass

    def onRegisterClicked(self):
        pass