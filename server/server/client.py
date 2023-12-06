import threading
import socket
import json
from .message_handler import handler

class Client:
    """
    The Client class represents a client connected to the server.

    Attributes:
        _conn (socket.socket): The client's socket connection.
        _address (str): The client's address.
        _name (str): The client's name.
        _state (bool): The client's state.
        _rooms (list): The rooms the client is in.
    """

    def __init__(self, conn, address, host, port, clients, server):
        """
        Initialize the Client with connection, address, host, port, clients list, and server.

        Args:
            conn (socket.socket): The client's socket connection.
            address (str): The client's address.
            host (str): The host address.
            port (int): The port number.
            clients (list): The list of clients.
            server (Server): The server.
        """
        self._conn = conn
        self._address = address
        self._name = ""
        self._state = None
        self._rooms = []
        
        ## Add client to clients list
        clients.append(self)

        ## Start handling client messages
        threading.Thread(target=handler, args=(self, clients, server)).start()

    ############################################################################################################

    @property
    def conn(self) -> socket.socket:
        return self._conn

    @property
    def addr(self) -> str:
        return self._address

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name:str):
        self._name = name

    @property
    def state(self) -> str:
        return self._state 
    @state.setter
    def state(self, state:str):
        self._state = state

    @property
    def rooms(self) -> list:
        return self._rooms
    @rooms.setter
    def rooms(self, rooms:str or list):
        """
        Set the rooms the client is in. If rooms is a string, it is converted to a list.

        Args:
            rooms (list or str): The rooms the client is in.

        Raises:
            TypeError: If rooms is not a list or a string.
        """
        if isinstance(rooms, str):
            rooms = [rooms]
        if not isinstance(rooms, list):
            raise TypeError("Rooms must be a list or a string")
        self._rooms = rooms

    ############################################################################################################

    def receive(self) -> str:
        """
        Receive data from the client.

        Returns:
            str: The received data.
        """
        return self._conn.recv(1024).decode()

    def send(self, data:str):
        """
        Send data to the client.

        Args:
            data (str): The data to send.
        """
        self._conn.send(data.encode())

    def close(self, clients:list):
        """
        Close the client's connection.
        """
        self._conn.close()
        clients.remove(self)
        
        
        
        