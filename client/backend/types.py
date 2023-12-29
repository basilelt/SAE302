## Import the types for documentation purposes
import logging

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
    client.close()

def handle_kick_message(client:'Client', message:dict):
    error = "You are kicked"
    timeout = message['timeout']
    reason = message['reason']
    client.error_received.emit(error, reason + "\n" + timeout)
    client.close()

def handle_ban_message(client:'Client', message:dict):
    error = "You are banned"
    reason = message['reason']
    client.error_received.emit(error, reason)
    client.close()

def handle_pending_room_message(client:'Client', message:dict):
    status = message['status']
    if status == 'ok':
        room = message['room']
        client.rooms.append(room)
        client.room_added.emit()
    elif status == 'error':
        reason = message['reason']
        client.error_received.emit(status, reason)

def handle_public_message(client:'Client', message:dict):
    print(message)
    if 'status' in message and message['status'] == 'error':
        reason = message['reason']
        client.error_received.emit('error', reason)
    elif 'room' in message and 'user' in message and 'message' in message:
        room = message['room']
        sender = message['user']
        content = message['message']
        client.public_message_received.emit(room, sender, content)
    else:
        print("Invalid message format")

def handle_private_message(client:'Client', message:dict):
    if message['status'] == 'ok':
        return
    elif message['status'] == 'error':
        reason = message['reason']
        client.error_received.emit(f"Error sending private", reason)

def handle_disconnect_message(client:'Client', message:dict):
    if message['status'] == "ok":
        logging.info("Disconnected")
        