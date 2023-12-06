import time
import socket
import logging
from .client import Client
from .database import DatabaseConnection

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from datetime import datetime

## Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    """
    The Server class handles the creation of the server and client management.

    Attributes:
        stop_server (bool): Flag to stop the server.
        stop_clients (bool): Flag to stop the clients.
        host (str): The host address.
        port (int): The port number.
        database (DatabaseConnection): The database connection.
    """

    def __init__(self, host:str, port:int):
        """
        Initialize the Server with host, port, and database connection.

        Args:
            host (str): The host address.
            port (int): The port number.
        """
        self.stop_server = False
        self.stop_clients = False
        self.host = host
        self.port = port
        self.clients = []
        self.rooms = []
        
        ## Initialize database connection
        self.database = DatabaseConnection()
        try:
            self.database.connect()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e

        ## Fetch rooms from database
        rooms = self.database.get_rooms()
        if rooms is not None:
            for room in rooms:
                self.rooms.append(room)

    def run(self):
        """
        Run the server. It creates the server socket and handles client connections.
        """
        try:
            ## Create server socket
            sock = self.create_socket()

            ## Handle client connections
            self.handle_clients(sock)
        except Exception as e:
            logging.error(f"Failed to run the server: {e}")

    def create_socket(self) -> socket.socket:
        """
        Create a socket for the server.

        Returns:
            sock: The created socket.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(1)
            return sock
        except Exception as e:
            logging.error(f"Failed to create a socket: {e}")
            raise e

    def handle_clients(self, sock:socket.socket):
        """
        Handle client connections.

        Args:
            sock (socket.socket): The server socket.
        """

        while not self.stop_server:
            try:
                ## Accept new client connection
                conn, address = sock.accept()

                ## Create new client
                client = Client(conn, address, self.host, self.port, self.clients, self)

                ## Add new client to clients list
                self.clients.append(client)
            except Exception as e:
                logging.error(f"Failed to handle a client: {e}")

        ## Close all client connections
        for client in self.clients:
            client.close()

        time.sleep(0.5)

        ## Close server socket
        sock.close()

    def close(self):
        """
        Close the server.
        """
        self.stop_server = True
        self.stop_clients = True
        self.database.close()
        
    def kick_user(self, username:str, timeout:'datetime', reason:str):
        """
        Kick a user from the server.

        Args:
            username (str): The username.
            timeout ('datetime'): Date and time when the user can join the server again.
            reason (str): The reason for kicking the user.
        """
        for client in self.clients:
            if client.name == username:
                self.database.execute_sql_query("UPDATE users SET state = 'kick', reason = %s, timeout = %s WHERE name = %s",
                                                (reason, timeout, username))
                
                client.state = 'kick'
                client.send({'type': 'kick',
                             'timeout': timeout.strftime("%Y-%m-%d %H:%M:%S"),
                             'reason': reason})
                break
    
    def ban_user(self, username:str, reason:str):
        """
        Ban a user from the server.

        Args:
            username (str): The username.
            reason (str): The reason for banning the user.
        """
        for client in self.clients:
            if client.name == username:
                self.database.execute_sql_query("UPDATE users SET state = 'ban', reason = %s WHERE name = %s",
                                                (reason, username))
                
                client.state = 'ban'
                client.send({'type': 'ban',
                             'reason': reason})
                break
    