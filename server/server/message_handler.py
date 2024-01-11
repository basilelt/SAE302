import logging
import json
from .types import *
# attention à votre nommage !

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client
    from .server import Server

def handler(client:'Client', clients:list, server:'Server'):
    """
    Handle client messages.

    :param Client client: The client.
    :param list clients: The list of clients.
    :param Server server: The server.
    """
    while not server.stop_clients:
        try:
            data = client.receive()
            ## Check if data is not empty, prevents errors when client closes
            if data:
                try:
                    message = json.loads(data)
                    handle_message(message, client, clients, server)
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON")
        except(ConnectionResetError):
            logging.error("Connection reset")
            break
        except(BrokenPipeError):
            logging.error("Connection broken")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break

def handle_message(message:dict, client:'Client', clients:list, server:'Server'):
    """
    Handle a specific type of message.

    :param dict message: The message.
    :param Client client: The client.
    :param list clients: The list of clients.
    :param Server server: The server.
    """
    message_handlers = {'signup':handle_signup_message,
                        'signin':handle_signin_message,
                        'disconnect':handle_disconnect_message,
                        'pending_room':handle_pending_room_message,
                        'public':handle_public_message,
                        'private':handle_private_message}

    ## Call the corresponding handler
    handler_message = message_handlers.get(message['type'])
    if handler_message:
        handler_message(message, client, clients, server)
    else:
        logging.error(f"Unknown message type: {message['type']}")
        
