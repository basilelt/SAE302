import logging
from .types import *

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

def handle_message(client:'Client', message:dict):
    """
    Handle a specific type of message.

    Args:
        client ('Client'): The client.
        message (dict): The message.
    """
    message_handlers = {
        'signup': handle_signup_message,
        'signin': handle_signin_message,
        'kill': handle_kill_message,
        'pending_room': handle_pending_room_message,
        'public': handle_public_message,
        'private': handle_private_message
    }

    ## Call the corresponding handler
    handler_message = message_handlers.get(message['type'])
    if handler_message:
        handler_message(client, message)
    else:
        logging.error(f"Unknown message type: {message['type']}")
        