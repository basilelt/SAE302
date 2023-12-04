import time, socket, logging
from .client import Client
from .database import DatabaseConnection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    def __init__(self, host:str, port:int):
        self.stop_server = False
        self.stop_clients = False
        self.host = host
        self.port = port

        self.database = DatabaseConnection()
        try:
            self.database.connect()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e

    #############################################################################

    def stop_db(self):
        self.database.close()

    def run(self):
        sock = self.create_socket()
        self.handle_clients(sock)

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(1)
        return sock

    def handle_clients(self, sock):
        clients = []
        while not self.stop_server:
            conn, address = sock.accept()
            client = Client(conn, address, self.host, self.port, clients, self)
            clients.append(client)

            cmd = input("")

            if cmd == '/stop':
                self.stop_server = True
                self.stop_clients = True
                for client in clients[:]:
                    client.close()
                    clients.remove(client)

        for client in clients:
            client.close()

        time.sleep(0.5)
        sock.close()