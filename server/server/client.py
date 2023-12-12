import threading
import logging
from .message_handler import handler

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .server import Server

class Client:
    """
    The Client class represents a client connected to the server.

    Attributes:
        conn (socket.socket): The client's socket connection.
        address (str): The client's address.
        name (str): The client's name.
        state (bool): The client's state.
        _rooms (list): The rooms the client is in.
    """

    def __init__(self, conn, address, host, port, clients, server):
        """
        Initialize the Client with connection, address, host, port, clients list, and server.

        Args:
            conn (socket.socket): The client's socket connection.
            address (str): The client's ip address.
            host (str): The host address.
            port (int): The port number.
            clients (list): The list of clients.
            server (Server): The server.
        """

        logging.info("Initializing client")
        self.conn = conn
        self.ip = address
        self.name = ""
        self.state = None
        self.pending_rooms = []
        self._rooms = []
        
        ## See if the client is already connected correctly
        self.login = False
        
        ## Add client to clients list
        clients.append(self)

        ## Start handling client messages
        threading.Thread(target=handler, args=(self, clients, server)).start()
        

    ############################################################################################################

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
        return self.conn.recv(1024).decode()

    def send(self, data:str):
        """
        Send data to the client.

        Args:
            data (str): The data to send.
        """
        self.conn.send(data.encode())

    def close(self, clients:list):
        """
        Close the client's connection.
        """
        logging.info("Closing client")
        
        self.conn.close()
        clients.remove(self)
        
    ############################################################################################################

    def addroom(self, server:'Server', room:str):
        """
        Add a room to the client's rooms list from the pending list.

        Args:
            server (Server): The server.
            room (str): The room to add.
        """
        self.pending_rooms.remove(room)
        server.database.execute_sql_query("UPDATE users SET pending_rooms = :pending_rooms WHERE name = :name",
                                          {'pending_rooms': ','.join(self.pending_rooms),
                                           'name': self.name})
        self.rooms.append(room)
        server.database.execute_sql_query("UPDATE users SET rooms = :rooms WHERE name = :name",
                                          {'rooms':','.join(self.rooms),
                                           'name':self.name})
