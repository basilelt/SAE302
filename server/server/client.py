import threading, socket
from .message_handler import handler

class Client:
    def __init__(self, conn, address, host, port, clients, server):
        self._conn = conn
        self.address = address

        self.name = ""
        self.state = False
        self.rooms = []

        clients.append(self)
        threading.Thread(target=handler, args=(self, host, port, clients, server)).start()

    #############################################################################

    @property
    def conn(self) -> socket.socket:
        return self._conn

    @property
    def addr(self) -> str:
        return self.address

    @property
    def name(self) -> str:
        return self.name
    @name.setter
    def name(self, name:str):
        self.name = name

    @property
    def state(self) -> bool:
        return self.state 
    @state.setter
    def state(self, state:bool):
        self.state = state

    @property
    def rooms(self) -> list:
        return self.rooms
    @rooms.setter
    def rooms(self, rooms):
        if isinstance(rooms, str):
            rooms = [rooms]
        if not isinstance(rooms, list):
            raise TypeError("Rooms must be a list or a string")
        self.rooms = rooms

    #############################################################################3

    def receive(self) -> str:
        return self._conn.recv(1024).decode()

    def send(self, data:str):
        self._conn.send(data.encode())

    def close(self):
        self._conn.close()