import threading, socket
from server.server.message_handler import handler

class Client:
    def __init__(self, conn, address, host, port, clients, server):
        self.__conn = conn
        self.__address = address

        ## Sera set par la connexion dans le thread
        self.__nom = ""
        self.__etat = ""
        self.__salon = []

        clients.append(self)
        threading.Thread(target=handler, args=(self, host, port, clients, server)).start()

    ## Getter de l'attribut conn
    @property
    def conn(self) -> socket.socket:
        return self.__conn
    
    ## Getter de l'attribut address
    @property
    def addr(self) -> str:
        return self.__address
    
    ## Getter et setter de l'attribut nom
    @property
    def nom(self) -> str:
        return self.__nom
    @nom.setter
    def nom(self, nom:str):
        self.__nom = nom

    ## Getter et setter de l'attribut etat
    @property
    def etat(self) -> bool:
        return self.__etat 
    @etat.setter
    def etat(self, etat:bool):
        self.__etat = etat

    ## Getter et setter de l'attribut salon
    @property
    def salon(self) -> list:
        return self.__salon
    @salon.setter
    def salon(self, salon):
        if isinstance(salon, list):
            self.__salon = salon
        elif isinstance(salon, str):
            self.__salon.append(salon)
        else:
            raise TypeError("Salon doit être une liste ou une chaîne de caractères")

    ## Méthode permettant de recevoir des données
    def receive(self) -> str:
        return self.__conn.recv(1024).decode()

    ## Méthode permettant d'envoyer des données
    def envoyer(self, data:str):
        self.__conn.send(data.encode())

    ## Méthode permettant de fermer la connexion
    def close(self):
        self.__conn.close()
        

