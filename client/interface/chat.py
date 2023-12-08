from PyQt6.QtWidgets import QMainWindow

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.client import Client
    
class ChatWindow(QMainWindow):
    def __init__(self, client:'Client'):
        pass
    
