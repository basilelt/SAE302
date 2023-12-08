## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

def handle_signup_message(client:'Client', message:dict):
    if message['status'] == "ok":
        client.isconnected = True
        print("Successfully signed up")
    elif message['status'] == "error":
        reason = message['reason']
    
def handle_signin_message(client:'Client', message:dict):
    if message['status'] == "ok":
        client.all_rooms = message['rooms'].split(',')
        client.rooms = message['rooms'].split(',')
        client.isconnected = True
        print("Successfully signed in")
    elif message['status'] == "error":
        reason = message['reason']
    elif message['status'] == "kick":
        timeout = message['timeout']
        reason = message['reason']
    elif message['status'] == "ban":
        reason = message['reason']
    
def handle_disconnect_message(client:'Client', message:dict):
    pass

def handle_pending_room_message(client:'Client', message:dict):
    pass

def handle_public_message(client:'Client', message:dict):
    pass

def handle_private_message(client:'Client', message:dict):
    pass
