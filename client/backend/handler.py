import logging
from .types import *

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

def handle_message(client:'Client', message:dict):
    """
    Handle a specific type of message.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    message_handlers = {'signup': handle_signup_message,
                        'signin': handle_signin_message,
                        'kill': handle_kill_message,
                        'kick': handle_kick_message,
                        'kick_ip': handle_kick_message,
                        'ban': handle_ban_message,
                        'ban_ip': handle_ban_message,
                        'pending_room': handle_pending_room_message,
                        'public': handle_public_message,
                        'private': handle_private_message,
                        'disconnect': handle_disconnect_message}

    ## Call the corresponding handler
    handler_message = message_handlers.get(message['type'])
    if handler_message:
        handler_message(client, message)
    else:
        logging.error(f"Unknown message type: {message['type']}")
        