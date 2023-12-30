### Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

import logging

def handle_signup_message(client:'Client', message:dict):
    """
    Handle a signup message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## If the status of the message is "ok"
    if message['status'] == "ok":
        ## Emit a connected signal from the client
        client.connected.emit()
    ## If the status of the message is "error"
    elif message['status'] == "error":
        ## Get the error and the reason from the message
        error = message['status']
        reason = message['reason']

        ## Emit an error received signal from the client with the error and the reason
        client.error_received.emit(error, reason)
    
def handle_signin_message(client:'Client', message:dict):
    """
    Handle a signin message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## If the status of the message is "ok"
    if message['status'] == "ok":
        ## Update the client's all_rooms and rooms attributes with the data from the message
        client.all_rooms = message['all_rooms']
        client.rooms = message['rooms']

        ## Emit a connected signal from the client
        client.connected.emit()
    ## If the status of the message is "error"
    elif message['status'] == "error":
        ## Get the error and the reason from the message
        error = message['status']
        reason = message['reason']

        ## Emit an error received signal from the client with the error and the reason
        client.error_received.emit(error, reason)
    ## If the status of the message is "kick"
    elif message['status'] == "kick":
        ## Get the error, the timeout, and the reason from the message
        error = message['status']
        timeout = message['timeout']
        reason = message['reason']

        ## Emit an error received signal from the client with the error and the reason concatenated with the timeout
        client.error_received.emit(error, reason + "\n" + timeout)
    ## If the status of the message is "ban"
    elif message['status'] == "ban":
        ## Get the error and the reason from the message
        error = message['status']
        reason = message['reason']

        ## Emit an error received signal from the client with the error and the reason
        client.error_received.emit(error, reason)
    
def handle_kill_message(client:'Client', message:dict):
    """
    Handle a kill message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## Close the client connection
    client.close()

def handle_kick_message(client:'Client', message:dict):
    """
    Handle a kick message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## Define the error message
    error = "You are kicked"

    ## Get the timeout and the reason from the message
    timeout = message['timeout']
    reason = message['reason']

    ## Emit an error received signal from the client with the error and the reason concatenated with the timeout
    client.error_received.emit(error, reason + "\n" + timeout)

    ## Close the client connection
    client.close()

def handle_ban_message(client:'Client', message:dict):
    """
    Handle a ban message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## Define the error message
    error = "You are banned"

    ## Get the reason from the message
    reason = message['reason']

    ## Emit an error received signal from the client with the error and the reason
    client.error_received.emit(error, reason)

    ## Close the client connection
    client.close()

def handle_pending_room_message(client:'Client', message:dict):
    """
    Handle a pending room message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## Get the status from the message
    status = message['status']

    ## If the status is 'ok'
    if status == 'ok':
        ## Get the room from the message
        room = message['room']

        ## Append the room to the client's rooms
        client.rooms.append(room)

        ## Emit a room added signal from the client
        client.room_added.emit()
    ## If the status is 'error'
    elif status == 'error':
        ## Get the reason from the message
        reason = message['reason']

        ## Emit an error received signal from the client with the status and the reason
        client.error_received.emit(status, reason)

def handle_public_message(client:'Client', message:dict):
    """
    Handle a public message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## If the message contains a 'status' key and its value is 'error'
    if 'status' in message and message['status'] == 'error':
        ## Get the reason from the message
        reason = message['reason']

        ## Emit an error received signal from the client with 'error' and the reason
        client.error_received.emit('error', reason)
    ## If the message contains 'room', 'user', and 'message' keys
    elif 'room' in message and 'user' in message and 'message' in message:
        ## Get the room, the sender, and the content from the message
        room = message['room']
        sender = message['user']
        content = message['message']

        ## Emit a public message received signal from the client with the room, the sender, and the content
        client.public_message_received.emit(room, sender, content)
    ## If the message does not contain the necessary keys
    else:
        ## Log an error message
        logging.error("Invalid public message received")

def handle_private_message(client:'Client', message:dict):
    """
    Handle a private message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## If the status of the message is 'ok'
    if message['status'] == 'ok':
        ## Return from the function
        return
    ## If the status of the message is 'error'
    elif message['status'] == 'error':
        ## Get the reason from the message
        reason = message['reason']

        ## Emit an error received signal from the client with the error message and the reason
        client.error_received.emit(f"Error sending private", reason)

def handle_disconnect_message(client:'Client', message:dict):
    """
    Handle a disconnect message from the client.

    :param client: The client.
    :type client: Client
    :param message: The message.
    :type message: dict
    """
    ## If the status of the message is 'ok'
    if message['status'] == "ok":
        ## Log an info message
        logging.info("Disconnected")
        