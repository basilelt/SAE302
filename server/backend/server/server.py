import threading, re, time, sys
from socket import socket as sock
from classes import Client

flag = False
flag2 = False

def server(host:str, port:int) -> None:
    global flag, flag2

    socket = sock.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket.bind((host, port))
    socket.listen(1)

    try:
        clients = []
        while not flag:
            conn, address = socket.accept()
            client = Client(conn, address, host, port, clients)
            clients.append(client)
            
    except(socket.gaierror):
        print("Erreur lors de la résolution de l'hôte")
    except(ConnectionRefusedError):
        print("Connexion refusée")
    except(TimeoutError):
        print("Timeout")
    except KeyboardInterrupt:
        print("Serveur en cours d'extinction...")
        flag = True
        flag2 = True
        for client in clients:
            client.close()
    except Exception as err:
        print(err)
    finally:
        time.sleep(0.5)
        socket.close()
        sys.exit()
