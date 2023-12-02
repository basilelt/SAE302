import threading, socket
from thread import handler

class Client:
    def __init__(self, conn, address, host, port, clients):
        self.__conn = conn
        self.__address = address
        self.__nom = ""
        self.__etat = ""
        self.__salon = []

        clients.append(self)
        threading.Thread(target=handler, args=(self, host, port, clients)).start()

    @property
    def conn(self) -> socket.socket:
        return self.__conn
    
    @property
    def addr(self) -> str:
        return self.__address
    
    @property
    def conn(self) -> list:
        return self.__salon
    
    @property
    def nom(self) -> str:
        return self.__nom
    @nom.setter
    def nom(self, nom:str):
        self.__nom = nom

    @property
    def etat(self) -> bool:
        return self.__etat 
    @etat.setter
    def etat(self, etat:bool):
        self.__etat = etat

    @property
    def salon(self) -> list:
        return self.__salon
    @salon.setter
    def salon(self, salon:list):
        if isinstance(salon, list):
            self.__salon = salon
        if isinstance(salon, str):
            self.__salon.append(salon)


    def receive(self) -> str:
        return self.__conn.recv(1024).decode()

    def envoyer(self, data:str):
        self.__conn.send(data)

