## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

def handle_signup_message():
    if message['status'] == "ok":
    pass

def handle_signin_message(client:'Client', message:dict):
    if message['status'] == "ok":
        client.login = True            
    elif message['status'] == "error":
        reason = message['reason']
    elif message['status'] == "kick":
        timeout = message['timeout']
        reason = message['reason']
    elif message['status'] == "ban":
        reason = message['reason']
    
def handle_disconnect_message():
    pass

def handle_pending_room_message():
    pass

def handle_public_message():
    pass

def handle_private_message():
    pass
