import socket
import threading
import json
import logging
from .handler import handle_message

## Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Client():
    def __init__(self, username:str, password:str, server:str, port:int, register:bool=False):
        self.username = username
        self.password = password
        self.server = server
        self.port = port

        self.listen_flag = False
        self.login = False

        self.__socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket_tcp.connect((self.server, self.port))

        if register:
            self.send_signup_info()
        
        else:
            self.send_login_info()

    def listen(self, socket:socket.socket):
        while not self.listen_flag:
            try:
                data = socket.recv(1024).decode()
                try:
                    message = json.loads(data)
                    handle_message(self, message)
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON")
            except(ConnectionResetError):
                logging.error("Connection reset")
            except(BrokenPipeError):
                logging.error("Connection broken")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

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


