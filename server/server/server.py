import time
import socket
import logging
from .client import Client
from .database import DatabaseConnection

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
        
        ## Initialize database connection
        self.database = DatabaseConnection()
        try:
            self.database.connect()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e

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
        clients = []
        while not self.stop_server:
            try:
                ## Accept new client connection
                conn, address = sock.accept()

                ## Create new client
                client = Client(conn, address, self.host, self.port, clients, self)

                ## Add new client to clients list
                clients.append(client)
            except Exception as e:
                logging.error(f"Failed to handle a client: {e}")

        ## Close all client connections
        for client in clients:
            client.close()

        time.sleep(0.5)

        ## Close server socket
        sock.close()
