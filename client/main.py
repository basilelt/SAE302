import sys
import logging
from PyQt6.QtWidgets import QApplication
from interface.login import LoginWindow

def main():
    ## Configure logging
    logging.basicConfig(filename='client.log', level=logging.INFO)

    ## Create the client
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()

    try:
        # Your code here
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Interrupted by keyboard")
        QApplication.quit()

if __name__ == "__main__":
    main()
