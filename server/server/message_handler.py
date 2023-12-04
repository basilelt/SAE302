import logging
import json
from .client import Client
from .server import Server
from .types import *

logging.basicConfig(filename='server.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def handler(client:Client, clients:list, server:Server) -> None:
    while not server.stop_clients:
        try:
            data = client.receive()
            message = json.loads(data)
            handle_message(message, client, clients, server)
        except(ConnectionResetError):
            logging.error("Connection reset")
        except(BrokenPipeError):
            logging.error("Connection broken")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

def handle_message(message, client, clients, server):
    if message['type'] == 'inscription':
        handle_inscription_message(message, client, server)
    elif message['type'] == 'connexion':
        handle_connexion_message(message, client, server)
    elif message['type'] == 'deconnexion':
        handle_deconnexion_message(client, clients)
    elif message['type'] == 'demande_salon':
        handle_demande_salon_message(message, client, server)
    elif message['type'] == 'text':
        handle_text_message(message, clients, client, server)
    elif message['type'] == 'private':
        handle_private_message(message, clients, client, server)

def handle_deconnexion_message(client, clients):
    client.close()
    clients.remove(client)
    