## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

def handle_signup_message(client:'Client', message:dict):
    if message['status'] == "ok":
        client.connected.emit()
    elif message['status'] == "error":
        error = message['status']
        reason = message['reason']
        client.error_received.emit(error, reason)
    
def handle_signin_message(client:'Client', message:dict):
    if message['status'] == "ok":
        client.all_rooms = message['all_rooms']
        client.rooms = message['rooms']
        client.connected.emit()
    elif message['status'] == "error":
        error = message['status']
        reason = message['reason']
        client.error_received.emit(error, reason)
    elif message['status'] == "kick":
        error = message['status']
        timeout = message['timeout']
        reason = message['reason']
        client.error_received.emit(error, reason + "\n" + timeout)
    elif message['status'] == "ban":
        error = message['status']
        reason = message['reason']
        client.error_received.emit(error, reason)
    
def handle_kill_message(client:'Client', message:dict):
    
    pass

def handle_pending_room_message(client:'Client', message:dict):
    pass

def handle_public_message(client:'Client', message:dict):
    pass

def handle_private_message(client:'Client', message:dict):
    pass
