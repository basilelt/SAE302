from PyQt6.QtCore import pyqtSignal, QObject
from socket import timeout
import socket
import threading
import json
import logging
from .handler import handle_message

class Client(QObject):
    """
    A QObject subclass that represents the client in the chat application.

    :param username: The username of the client.
    :type username: str
    :param password: The password of the client.
    :type password: str
    :param server: The server that the client will connect to.
    :type server: str
    :param port: The port that the client will connect to.
    :type port: int
    """
    ## Signals
    connected = pyqtSignal()
    error_received = pyqtSignal(str, str)
    room_added = pyqtSignal()
    public_message_received = pyqtSignal(str, str, str)
    connection_failed = pyqtSignal()

    def __init__(self, username:str, password:str, server:str, port:int):
        """
        Initialize the Client.

        :param username: The username of the client.
        :type username: str
        :param password: The password of the client.
        :type password: str
        :param server: The server that the client will connect to.
        :type server: str
        :param port: The port that the client will connect to.
        :type port: int
        """
        super().__init__()

        ## Set the username, password, server, and port
        self.username = username
        self.password = password
        self.server = server
        self.port = port

        ## Initialize the listen flag to False
        self.listen_flag = False

        ## Initialize the all_rooms and rooms lists
        self.all_rooms = []
        self.rooms = []

        ## Create a new TCP socket
        self.__socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self, register:bool=False):
        """
        Connect the client to the server.

        :param register: Whether to register a new account or not.
        :type register: bool
        """
        ## Try to connect to the server
        try:
            self.__socket_tcp.connect((self.server, self.port))
        except ConnectionRefusedError:
            ## If the connection is refused, emit an error message and return
            logging.error('ConnectionRefusedError: The server is unreachable.')
            self.error_received.emit("ConnectionRefusedError", "The server is unreachable.")
            return

        ## Start a new thread to listen for messages from the server
        self.thread_listen = threading.Thread(target=self.listen, args=(self.__socket_tcp,))
        self.thread_listen.start()

        ## If the register flag is True, send signup info
        if register:
            self.send_signup_info()
        ## If the register flag is False, send login info
        else:
            self.send_login_info()

    def listen(self, socket:socket.socket):
        """
        Listen for messages from the server.

        :param socket: The socket to listen on.
        :type socket: socket.socket
        """
        ## Set a timeout of 1 second on the socket
        socket.settimeout(1)

        ## While the listen flag is False
        while not self.listen_flag:
            try:
                ## Try to receive data from the socket
                data = socket.recv(1024).decode()

                ## If data was received
                if data:
                    logging.info('Data received from server.')
                    try:
                        ## Try to parse the data as JSON
                        message = json.loads(data)

                        ## Handle the message
                        handle_message(self, message)
                    except json.JSONDecodeError:
                        ## If the data is not valid JSON, log an error
                        logging.error("Failed to decode JSON")
            except timeout:
                ## If a timeout occurs, continue to the next iteration of the loop
                continue
            except ConnectionResetError:
                ## If the connection is reset, log an error and emit a connection failed signal
                logging.error("Connection reset")
                self.connection_failed.emit()
                break
            except BrokenPipeError:
                ## If a broken pipe error occurs, log an error and emit a connection failed signal
                logging.error("Broken pipe")
                self.connection_failed.emit()
                break
            except Exception as e:
                ## If any other exception occurs, log an error and emit a connection failed signal
                logging.error(f"Unexpected error: {e}")
                self.connection_failed.emit()
                break
    
    def send_pending_room(self, room:str):
        """
        Send a pending room to the server.

        :param room: The name of the room.
        :type room: str
        """
        ## Create a dictionary with the type of the message and the room name
        data = {'type':'pending_room',
                'room':room}

        ## Convert the dictionary to a JSON string and encode it to bytes
        ## Then send it to the server using the TCP socket
        self.__socket_tcp.send(json.dumps(data).encode())

    def send_signup_info(self):
        """
        Send signup information to the server.
        """
        ## Create a dictionary with the type of the message and the username and password
        data = {'type':'signup',
                'username':self.username,
                'password':self.password}

        ## Convert the dictionary to a JSON string and encode it to bytes
        ## Then send it to the server using the TCP socket
        self.__socket_tcp.send(json.dumps(data).encode())

    def send_login_info(self):
        """
        Send login information to the server.
        """
        ## Create a dictionary with the type of the message and the username and password
        data = {'type':'signin',
                'username':self.username,
                'password':self.password}

        ## Convert the dictionary to a JSON string and encode it to bytes
        ## Then send it to the server using the TCP socket
        self.__socket_tcp.send(json.dumps(data).encode())
    
    def send_public_message(self, room:str, message:str):
        """
        Send a public message to a room.

        :param room: The name of the room.
        :type room: str
        :param message: The message to send.
        :type message: str
        """
        ## Create a dictionary with the type of the message, the room name, and the message
        data = {'type':'public',
                'room':room,
                'message':message}

        ## Convert the dictionary to a JSON string and encode it to bytes
        ## Then send it to the server using the TCP socket
        self.__socket_tcp.send(json.dumps(data).encode())
    
    def send_private_message(self, username:str, message:str):
        """
        Send a private message to a user.

        :param username: The username of the recipient.
        :type username: str
        :param message: The message to send.
        :type message: str
        """
        ## Create a dictionary with the type of the message, the recipient's username, the sender's username, and the message
        private_message = {'type':'private',
                        'to':username,
                        'user':self.username,
                        'message':message}

        ## Convert the dictionary to a JSON string and encode it to bytes
        ## Then send it to the server using the TCP socket
        self.__socket_tcp.send(json.dumps(private_message).encode())
    
    def close(self):
        """
        Close the connection to the server.
        """
        ## Set the listen flag to True to stop the listening loop
        self.listen_flag = True

        try:
            ## Check if the socket is connected
            self.__socket_tcp.getpeername()

            ## Send a disconnect message to the server
            self.__socket_tcp.send(json.dumps({'type':'disconnect'}).encode())
        except OSError:
            ## If the socket is not connected, pass
            logging.error("Socket is not connected")
            pass

        ## If a listening thread exists, wait for it to finish
        if hasattr(self, 'thread_listen'):
            self.thread_listen.join()

        ## Close the socket
        logging.info('Connection to server closed.')
        self.__socket_tcp.close()
