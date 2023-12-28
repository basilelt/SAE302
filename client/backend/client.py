from PyQt6.QtCore import pyqtSignal, QObject
import socket
from socket import timeout
import threading
import json
import logging
from .handler import handle_message

## Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Client(QObject):
    connected = pyqtSignal()
    error_received = pyqtSignal(str, str)
    room_added = pyqtSignal()
    public_message_received = pyqtSignal(str, str, str)
    connection_failed = pyqtSignal()

    def __init__(self, username:str, password:str, server:str, port:int):
        super().__init__()
        self.username = username
        self.password = password
        self.server = server
        self.port = port

        self.listen_flag = False

        self.all_rooms = []
        self.rooms = []

        self.__socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        

    def connect(self, register:bool=False):
        try:
            self.__socket_tcp.connect((self.server, self.port))
        except ConnectionRefusedError:
            self.error_received.emit("ConnectionRefusedError", "The server is unreachable.")
            return

        self.thread_listen = threading.Thread(target=self.listen, args=(self.__socket_tcp,))
        self.thread_listen.start()

        if register:
            self.send_signup_info()
        
        else:
            self.send_login_info()

    def listen(self, socket:socket.socket):
        socket.settimeout(1)
        while not self.listen_flag:
            try:
                data = socket.recv(1024).decode()
                if data: 
                    try:
                        message = json.loads(data)
                        print(message)
                        handle_message(self, message)
                    except json.JSONDecodeError:
                        logging.error("Failed to decode JSON")
            except(timeout):
                continue
            except(ConnectionResetError):
                logging.error("Connection reset")
                self.connection_failed.emit()
                break
            except(BrokenPipeError):
                logging.error("Broken pipe")
                self.connection_failed.emit()
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                self.connection_failed.emit()
                break
    
    def send_pending_room(self, room:str):
        data = {'type': 'pending_room',
                'room': room}
        self.__socket_tcp.send(json.dumps(data).encode())

    def send_signup_info(self):
        data = {'type': 'signup',
                'username': self.username,
                'password': self.password}
        self.__socket_tcp.send(json.dumps(data).encode())

    def send_login_info(self):
        data = {'type': 'signin',
                'username': self.username,
                'password': self.password}
        self.__socket_tcp.send(json.dumps(data).encode())
    
    def send_public_message(self, room:str, message:str):
        data = {'type': 'public',
                'room': room,
                'message': message}
        self.__socket_tcp.send(json.dumps(data).encode())
    
    def close(self):
        self.listen_flag = True
        try:
            self.__socket_tcp.getpeername()
            self.__socket_tcp.send(json.dumps({'type': 'disconnect'}).encode())
        except OSError:
            pass  # Socket is not connected
        if hasattr(self, 'thread_listen'):
            self.thread_listen.join()
        self.__socket_tcp.close()
