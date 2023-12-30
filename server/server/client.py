import threading
import logging
import json
from .message_handler import handler

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .server import Server
    import socket

class Client:
    """
    The Client class represents a client connected to the server.

    :ivar socket.socket conn: The client's socket connection.
    :ivar str address: The client's address.
    :ivar str name: The client's name.
    :ivar bool state: The client's state.
    :ivar list _rooms: The rooms the client is in.
    """
    def __init__(self, conn:'socket.socket', address:str, host:str, port:int, clients:list, server:'Server'):
        """
        Initialize the Client with connection, address, host, port, clients list, and server.

        :param 'socket.socket' conn: The client's socket connection.
        :param str address: The client's IP address.
        :param str host: The host address.
        :param int port: The port number.
        :param list clients: The list of clients.
        :param 'Server' server: The server.
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
        """
        Get the rooms the client is in.

        :return: The rooms the client is in.
        :rtype: list
        """
        return self._rooms
    @rooms.setter
    def rooms(self, rooms:str or list):
        """
        Set the rooms the client is in. If rooms is a string, it is converted to a list.

        :param list or str rooms: The rooms the client is in.
        :raises TypeError: If rooms is not a list or a string.
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

        :return: The received data.
        :rtype: str
        """
        return self.conn.recv(1024).decode()

    def send(self, data:str):
        """
        Send data to the client.

        :param str data: The data to send.
        """
        self.conn.send(data.encode())

    def close(self, clients:list):
        """
        Close the client's connection.

        :param list clients: The list of clients.
        """
        logging.info("Closing client")
        
        self.conn.close()
        clients.remove(self)
        
    ############################################################################################################

    def addroom(self, server:'Server', room:str):
        """
        Add a room to the client's rooms list from the pending list.

        :param Server server: The server.
        :param str room: The room to add.
        """
        if room in self.pending_rooms:
            self.pending_rooms.remove(room)
            server.database.execute_sql_query("UPDATE users SET pending_rooms = :pending_rooms WHERE name = :name",
                                              {'pending_rooms':','.join(self.pending_rooms),
                                               'name':self.name})
        self.rooms.append(room)
        server.database.execute_sql_query("INSERT INTO belong (user, room) VALUES (:user, :room)",
                                          {'user':self.name,
                                           'room':room})
        
        self.send(json.dumps({'type':'pending_room',
                              'status':'ok',
                              'room':room}))
