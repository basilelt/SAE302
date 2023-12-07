## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

def handle_signup_message():

    pass

def handle_signin_message(client:'Client', message:dict):
    if message['type'] == "signin":
        if message['status'] == "ok":
            client.login = True
            
            print(f"{client.name} has logged in")
        return
    pass

def handle_disconnect_message():
    pass

def handle_pending_room_message():
    pass

def handle_public_message():
    pass

def handle_private_message():
    pass
