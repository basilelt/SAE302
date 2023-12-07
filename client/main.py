import sys
import logging
from PyQt6.QtWidgets import QApplication
from interface.login import LoginWindow


def main():
    ## Configure logging
    logging.basicConfig(filename='server.log', level=logging.INFO)

    ## Start the client
    app = QApplication(sys.argv)
    
    login = LoginWindow()
    login.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
