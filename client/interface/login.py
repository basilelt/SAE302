from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLineEdit, QLabel, QGridLayout, QFrame, QGroupBox, QVBoxLayout, QGraphicsDropShadowEffect, QApplication, QDialog
from PyQt6.QtCore import Qt, QPropertyAnimation, QSize, QSequentialAnimationGroup
from PyQt6.QtGui import QPalette, QColor, QShowEvent, QKeyEvent, QMovie
import os
from backend.client import Client
from .chat import ChatWindow

import logging

class LoginWindow(QMainWindow):
    """
    A class to represent a login window.

    ...

    :attr animationGroup: a group of animations that will be played sequentially.
    :type animationGroup: QSequentialAnimationGroup
    :attr connectOriginalSize: the original size of the connect button.
    :type connectOriginalSize: QSize
    :attr quitOriginalSize: the original size of the quit button.
    :type quitOriginalSize: QSize
    :attr registerOriginalSize: the original size of the register button.
    :type registerOriginalSize: QSize

    :method setupCSS(): Sets up the CSS for the window.
    :method setupWidgets(): Sets up the widgets for the window.
    :method createLineEdit() -> QLineEdit: Creates a QLineEdit widget with a specific style.
    :method createGroup(labelText: str, lineEdit: QLineEdit) -> QGroupBox: Creates a QGroupBox with a QLabel and a QLineEdit.
    :method setupLayout(): Sets up the layout for the window.
    :method setupAnimations(): Sets up the animations for the buttons.
    :method showEvent(event: QShowEvent): Overrides the showEvent method to set up the button animations.
    :method animateButton(button: QPushButton, animation: QPropertyAnimation, originalSize: QSize): Animates a button when it is clicked.
    :method keyPressEvent(event: QKeyEvent): Overrides the keyPressEvent method to handle Return and Enter key presses.
    :method onConnectClicked(): Handles the click event of the connect button.
    :method onQuitClicked(): Handles the click event of the quit button.
    :method onRegisterClicked(): Handles the click event of the register button.
    """
    def __init__(self):
        """
        Initializes the LoginWindow.

        This method initializes the QMainWindow parent class, sets up some basic window properties, and calls the setup methods to initialize CSS, widgets, layout, and animations.
        """
        super().__init__()
        self.client = None

        ## Initialize the QMainWindow parent class and set up some basic window properties
        self.animationGroup = None
        self.setMinimumWidth(600)
        self.setWindowTitle("Login to a chat server")

        ## Call the setup methods to initialize CSS, widgets, layout, and animations
        self.setupCSS()
        self.setupWidgets()
        self.setupLayout()
        self.setupAnimations()

        self.connect.clicked.connect(self.onConnectClicked)
        self.quit.clicked.connect(self.onQuitClicked)
        self.register.clicked.connect(self.onRegisterClicked)

    def setupCSS(self):
        """
        Sets up the CSS for the window.

        This method reads a CSS file, formats it with color values, and applies it to the window.
        """
        ## Get the color palette of the window
        window_color = self.palette().color(QPalette.ColorRole.Window)
        darker_color = window_color.darker(120)
        text_color = self.palette().color(QPalette.ColorRole.Text)
        
        ## Read the CSS file
        css_file_path = os.path.join(os.path.dirname(__file__), 'login.css')
        with open(css_file_path, 'r') as f:
            css = f.read()
        
        ## Format the CSS with the color values
        css = css.format(darker_color.name(),
                         darker_color.darker(150).name(),
                         darker_color.lighter(110).name(),
                         text_color.name(),
                         window_color.name())

        ## Apply the CSS to the window
        self.setStyleSheet(css)

    def setupWidgets(self):
        """
        Sets up the widgets for the window.

        This method creates QLineEdit widgets for user, password, server, and port. It also creates QPushButton widgets for connect, quit, and register. Finally, it creates QGroupBox widgets for user, password, server, and port.
        """
        ## Create line edits for user, password, server, and port
        self.__user = self.createLineEdit()
        self.__password = self.createPasswordLineEdit()
        self.__server = self.createLineEdit()
        self.__server.setText("localhost")
        self.__port = self.createLineEdit()
        self.__port.setText("5000")

        ## Create buttons for connect, quit, and register
        self.connect = QPushButton("Connect")
        self.quit = QPushButton("Quit")
        self.register = QPushButton("Register")

        ## Create groups for user, password, server, and port
        self.userGroup = self.createGroup("Username:", self.__user)
        self.passwordGroup = self.createGroup("Password:", self.__password)
        self.serverGroup = self.createGroup("Server address:", self.__server)
        self.portGroup = self.createGroup("Server port:", self.__port)

    def createLineEdit(self):
        """
        Creates a QLineEdit widget with a specific style.

        This method creates a QLineEdit widget and sets its background color and border style.

        :returns: The created QLineEdit widget.
        :rtype: QLineEdit
        """
        ## Create a QLineEdit widget
        lineEdit = QLineEdit()
        window_color = self.palette().color(QPalette.ColorRole.Window)
        darker_color = window_color.darker(120)

        ## Set the style of the QLineEdit
        lineEdit.setStyleSheet(f"background-color: {darker_color.darker(110).name()}; border: none")
        return lineEdit
    
    def createPasswordLineEdit(self):
        """
        Creates a QLineEdit widget with a specific style for password input.

        This method creates a QLineEdit widget, sets its background color and border style, and sets its echo mode to Password.
        """
        line_edit = self.createLineEdit()
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        return line_edit

    def createGroup(self, labelText:str, lineEdit:QLineEdit) -> QGroupBox:
        """
        Creates a QGroupBox with a QLabel and a QLineEdit.

        This method creates a QLabel with the given text and aligns it to the center. It then creates a QGroupBox and sets its layout to a QVBoxLayout. Finally, it adds the label and line edit to the layout.

        :param labelText: The text for the QLabel.
        :type labelText: str
        :param lineEdit: The QLineEdit to add to the QGroupBox.
        :type lineEdit: QLineEdit
        :returns: The created QGroupBox.
        :rtype: QGroupBox
        """
        ## Create a QLabel with the given text and align it to the center
        label = QLabel(labelText)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("border: none")

        ## Create a QGroupBox and set its layout to a QVBoxLayout
        group = QGroupBox()
        layout = QVBoxLayout(group)

        ## Add the label and line edit to the layout
        layout.addWidget(label)
        layout.addWidget(lineEdit)
        return group

    def setupLayout(self):
        """
        Sets up the layout for the window.

        This method creates a QWidget and sets it as the central widget of the window. It then creates a QGridLayout and sets it as the layout of the central widget. It also creates a QFrame, sets its style and minimum width, and adds it to the grid layout.
        """
        ## Create a QWidget and set it as the central widget of the window
        widget = QWidget()
        self.setCentralWidget(widget)

        ## Create a QGridLayout and set it as the layout of the central widget
        grid = QGridLayout()
        widget.setLayout(grid)

        ## Create a QFrame and set its style
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        frame.setMinimumWidth(400)

        ## Create a QGridLayout for the frame
        frameLayout = QGridLayout(frame)

        ## Add the groups and buttons to the frame layout
        frameLayout.addWidget(self.userGroup, 0, 0, 1, 2)
        frameLayout.addWidget(self.passwordGroup, 1, 0, 1, 2)
        frameLayout.addWidget(self.serverGroup, 2, 0, 1, 2)
        frameLayout.addWidget(self.portGroup, 3, 0, 1, 2)
        frameLayout.addWidget(self.connect, 4, 0)
        frameLayout.addWidget(self.quit, 4, 1)
        frameLayout.addWidget(self.register, 5, 0, 1, 2)

        ## Set the stretch factors of the grid layout
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(2, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(2, 1)

        ## Add the frame to the grid layout
        grid.addWidget(frame, 1, 1)        

    def setupAnimations(self):
        """
        Sets up the animations for the buttons.

        This method creates QPropertyAnimation objects for the connect, quit, and register buttons. It also creates a QSequentialAnimationGroup and adds the animations to it.
        """
        ## Create animations for the connect, quit, and register buttons
        self.connectAnimation = QPropertyAnimation(self.connect, b"geometry")
        self.quitAnimation = QPropertyAnimation(self.quit, b"geometry")
        self.registerAnimation = QPropertyAnimation(self.register, b"geometry")

        ## Connect the clicked signal of the buttons to the animateButton method
        self.connect.clicked.connect(lambda: self.animateButton(self.connect, self.connectAnimation, self.connectOriginalSize))
        self.quit.clicked.connect(lambda: self.animateButton(self.quit, self.quitAnimation, self.quitOriginalSize))
        self.register.clicked.connect(lambda: self.animateButton(self.register, self.registerAnimation, self.registerOriginalSize))

    def showEvent(self, event:QShowEvent):
        """
        Overrides the showEvent method to set up the button animations.

        This method saves the original sizes of the connect, quit, and register buttons. It also connects the clicked signal of each button to a lambda function that calls the animateButton method.

        :param event: The show event.
        :type event: QShowEvent
        """
        ## Store the original sizes of the buttons
        self.connectOriginalSize = self.connect.size()
        self.quitOriginalSize = self.quit.size()
        self.registerOriginalSize = self.register.size()

        ## Connect the clicked signal of the buttons to the animateButton method
        self.connect.clicked.connect(lambda: self.animateButton(self.connect, self.connectAnimation, self.connectOriginalSize))
        self.quit.clicked.connect(lambda: self.animateButton(self.quit, self.quitAnimation, self.quitOriginalSize))
        self.register.clicked.connect(lambda: self.animateButton(self.register, self.registerAnimation, self.registerOriginalSize))


    def animateButton(self, button:QPushButton, animation:QPropertyAnimation, originalSize:QSize):
        """
        Animates a button when it is clicked.

        This method creates a QGraphicsDropShadowEffect, sets its properties, and applies it to the button. It then starts the animation and sets a timer to remove the effect after the animation is finished.

        :param button: The button to animate.
        :type button: QPushButton
        :param animation: The animation to apply to the button.
        :type animation: QPropertyAnimation
        :param originalSize: The original size of the button.
        :type originalSize: QSize
        """
        ## If the animation is running, stop it
        if animation.state() == QPropertyAnimation.State.Running:
            animation.stop()

        ## Create a drop shadow effect for the button
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 255))
        shadow.setOffset(0)
        button.setGraphicsEffect(shadow)

        ## Create animations for the blur radius of the shadow
        blurAnimation = QPropertyAnimation(shadow, b"blurRadius")
        blurAnimation.setStartValue(10)
        blurAnimation.setEndValue(0)
        blurAnimation.setDuration(100)
        
        ## Create an animation for the color of the shadow
        colorAnimation = QPropertyAnimation(shadow, b"color")
        colorAnimation.setStartValue(QColor(0, 0, 0, 255))
        colorAnimation.setEndValue(QColor(0, 0, 0, 0))
        colorAnimation.setDuration(1000)

        ## Create an animation for the size of the button
        sizeAnimation = QPropertyAnimation(button, b"size")
        sizeAnimation.setStartValue(originalSize)
        sizeAnimation.setEndValue(originalSize - QSize(10, 10))
        sizeAnimation.setDuration(100)
        sizeAnimation.setEndValue(originalSize)

        ## Create a QSequentialAnimationGroup and add the animations to it
        self.animationGroup = QSequentialAnimationGroup()
        self.animationGroup.addAnimation(sizeAnimation)
        self.animationGroup.addAnimation(blurAnimation)
        self.animationGroup.addAnimation(colorAnimation)
        
        ## Start the animation group
        self.animationGroup.start()
        self.animationGroup.finished.connect(lambda: button.setGraphicsEffect(None))

    def keyPressEvent(self, event:QKeyEvent):
        """
        Overrides the keyPressEvent method to handle Return and Enter key presses.

        This method checks if the pressed key is Return or Enter. If the user line edit has focus, it sets the focus to the password line edit. If the password line edit has focus, it sets the focus to the server line edit. If the server line edit has focus, it sets the focus to the port line edit. If the port line edit has focus, it clicks the connect button.

        :param event: The key press event.
        :type event: QKeyEvent
        """
        ## Check if the pressed key is Return or Enter
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            ## If the user line edit has focus, move the focus to the next line edit
            if self.__user.hasFocus():
                self.__password.setFocus()
            elif self.__password.hasFocus():
                self.__server.setFocus()
            elif self.__server.hasFocus():
                self.__port.setFocus()
            ## If the port line edit hasFocus, click the connect button
            elif self.__port.hasFocus():
                self.connect.click()
                
    def onConnectClicked(self):
        """
        Handles the click event of the connect button.
        """
        try:
            username = self.__user.text()
            password = self.__password.text()
            server = self.__server.text()
            port = int(self.__port.text())
            self.client = Client(username, password, server, port)

            self.client.connected.connect(self.onClientConnected)
            self.client.connection_failed.connect(self.handle_disconnection)
            self.client.error_received.connect(self.showErrorPopup)

            self.client.connect()
        except Exception as err:
            logging.error(f"Failed to connect to the server: {err}")

    def onClientConnected(self):
        """
        Handles the connected signal of the client.
        """
        self.chat_window = ChatWindow(self.client)
        self.chat_window.show()
        self.hide()

        self.client.room_added.connect(self.chat_window.refresh_rooms)

    def onQuitClicked(self):
        """
        Handles the click event of the quit button.
        """
        if self.client != None:
            self.client.close()
        QApplication.exit(0)

    def closeEvent(self, event):
        """
        Overrides the closeEvent method to close the client.
        """
        self.client.close()
        event.accept()
        
    def onRegisterClicked(self):
        """
        Handles the click event of the register button.
        """
        try:
            username = self.__user.text()
            password = self.__password.text()
            server = self.__server.text()
            port = int(self.__port.text())
            self.client = Client(username, password, server, port)

            self.client.connection_failed.connect(self.handle_disconnection)
            self.client.error_received.connect(self.showErrorPopup)

            self.client.connect(register=True)
        except Exception as err:
            logging.error(f"Failed to register: {err}")

    def handle_disconnection(self):
        """
        Handles the disconnection of the client.
        """
        ## Show the login window and hide the chat window
        if self.chat_window is not None:
            self.chat_window.hide()
        self.show()

    def showErrorPopup(self, error:str, error_message:str):
        """
        Show an error dialog with a given title and message.

        This function creates a QDialog with a specified error title and message.
        It also displays an error gif in the dialog. The dialog has an "OK" button
        that closes the dialog when clicked.

        :param error: The title of the error dialog.
        :type error: str
        :param error_message: The message to display in the error dialog.
        :type error_message: str
        """
         # Create a new dialog
        dialog = QDialog()
        dialog.setWindowTitle(error)
        dialog.setFixedSize(200, 300)

        # Set up the error gif
        gif_path = os.path.join(os.path.dirname(__file__), 'error.gif')
        gif = QMovie(gif_path)
        gif.setScaledSize(QSize(140, 249))
        gif_label = QLabel()
        gif_label.setMovie(gif)
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif.start()

        # Set up the error message
        text_label = QLabel(error_message)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set up the "OK" button
        okButton = QPushButton("OK")
        okButton.clicked.connect(dialog.accept)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(gif_label)
        layout.addWidget(text_label)
        layout.addWidget(okButton)
        dialog.setLayout(layout)

        # Show the dialog
        dialog.exec()
