import threading, socket
from thread import handler

class Client:
    def __init__(self, conn, address, host, port, clients):
        self.__conn = conn
        self.__address = address
        self.__nom = ""        

        threading.Thread(target=handler, args=(self, host, port, clients)).start()

    @property
    def conn(self) -> socket.socket:
        return self.__conn
    
    @property
    def nom(self) -> bool:
        return self.__nom
    @nom.setter
    def etat(self, etat:bool):
        self.__etat = etat

    @property
    def etat(self) -> bool:
        return self.__etat 
    @etat.setter
    def etat(self, etat:bool):
        self.__etat = etat

