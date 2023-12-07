import logging
import json
from .types import *

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client
    from .server import Server

def handler(client:'Client', clients:list, server:'Server'):
    """
    Handle client messages.

    Args:
        client ('Client'): The client.
        clients (list): The list of clients.
        server ('Server'): The server.
    """
    while not server.stop_clients:
        try:
            data = client.receive()
            try:
                message = json.loads(data)
                print(message)
                handle_message(message, client, clients, server)
            except json.JSONDecodeError:
                logging.error("Failed to decode JSON")
        except(ConnectionResetError):
            logging.error("Connection reset")
        except(BrokenPipeError):
            logging.error("Connection broken")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

def handle_message(message:dict, client:'Client', clients:list, server:'Server'):
    """
    Handle a specific type of message.

    Args:
        message (dict): The message.
        client ('Client'): The client.
        clients (list): The list of clients.
        server ('Server'): The server.
    """
    message_handlers = {
        'signup': handle_signup_message,
        'signin': handle_signin_message,
        'disconnect': handle_disconnect_message,
        'pending_room': handle_pending_room_message,
        'public': handle_public_message,
        'private': handle_private_message
    }

    ## Call the corresponding handler
    handler_message = message_handlers.get(message['type'])
    if handler_message:
        handler_message(message, client, clients, server)
    else:
        logging.error(f"Unknown message type: {message['type']}")
        