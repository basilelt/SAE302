import json
import datetime
import bcrypt

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client
    from .server import Server

def handle_signup_message(message:dict, client:'Client', _:list, server:'Server'):
    """
    Handle signup message from the client.

    Args:
        message (dict): The signup message.
        client ('Client'): The client.
        server ('Server'): The server.
    """
    user = message['username']
    password = message['password'].encode('utf-8')

    ## Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)

    ## Check if the user already exists
    if not server.database.user_exists(user):
        client.name = user

        creation_date = datetime.datetime.now()
        try:
            server.database.execute_sql_query("INSERT INTO users (name, password, date_creation) VALUES (?, ?, ?)",
                                              (user, hashed_password, creation_date))
            client.login = True
            response = json.dumps({'type': 'signup',
                                   'status': 'ok'})
        except Exception as e:
            response = json.dumps({'type': 'signup',
                                   'status': 'error',
                                   'reason': str(e)})
    else:
        response = json.dumps({'type': 'signup',
                               'status': 'error',
                               'reason': 'username_already_used'})

    client.send(response)

################################################################################################################

def handle_signin_message(message:dict, client:'Client', clients:list, server:'Server'):
    """
    Handle signin message from the client.

    Args:
        message (dict): The signin message.
        client ('Client'): The client.
        server ('Server'): The server.
    """
    user = message['username']
    password = message['password'].encode('utf-8')

    if server.database.user_exists(user):
        hashed_password = server.database.fetch_user_password(user)

        if not bcrypt.checkpw(password, hashed_password): 
            ## Incorrect password
            response = json.dumps({'type': 'signin',
                                   'status': 'error',
                                   'reason': 'incorrect_password'})
            client.send(response)
        else:
            client.name = user
            client.state = server.database.fetch_user_state(user)
                     
            result = server.database.fetch_all("SELECT name FROM rooms, users WHERE users.name = ?",
                                               (user,))
            client.rooms = result if result else None

            result = server.database.fetch_all("SELECT pending_rooms FROM users WHERE users.name = ?",
                                               (user,))
            client.pending_rooms = result if result else None

            if client.state == "valid":
                ## Valid user
                response = json.dumps({'type': 'signin',
                                       'status': 'ok'})
                client.login = True
                client.send(response)
                                  
            elif client.state == "kick":
                ## Kicked user
                result = server.database.fetch_one("SELECT timeout FROM users WHERE name = ?",
                                                   (user,))
                timeout = result[0][0] if result else None

                result = server.database.fetch_one("SELECT reason FROM users WHERE name = ?",
                                                   (user,))
                reason = result[0][0] if result else None

                response = json.dumps({'type': 'signin',
                                       'status': 'kick',
                                       'timeout': timeout,
                                       'reason': reason})
                client.send(response)
                client.close(clients)
                                     
            elif client.state == "ban":
                ## Banned user
                result = server.database.fetch_one("SELECT reason FROM users WHERE name = ?",
                                                   (user,))
                reason = result[0][0] if result else None

                response = json.dumps({'type': 'signin',
                                       'status': 'ban',
                                       'reason': reason})
                client.send(response)
                client.close(clients)
    
    else:
        ## Non-existent user
        response = json.dumps({'type': 'signin',
                               'status': 'error',
                               'reason': 'incorrect_username'})
        client.send(response)

################################################################################################################

def handle_disconnect_message(_1:dict, client:'Client', clients:list, _2:'Server'):
    """
    Handle disconnect message from the client.

    Args:
        client ('Client'): The client.
        clients (list): The list of all clients.
    """
    try:
        ## Close the client connection and remove it from the list of clients
        client.close()
        clients.remove(client)
    except ValueError:
        ## Handle the case where the client is not in the list
        print(f"Failed to remove client {client.name} from the list.")
    except Exception as e:
        ## Handle any other unexpected errors
        print(f"Unexpected error: {e}")

################################################################################################################

def handle_pending_room_message(message:dict, client:'Client', _:list, server:'Server'):
    """
    Handle pending room message from the client.

    Args:
        message (dict): The pending room message.
        client ('Client'): The client.
        server ('Server'): The server.
    """
    if client.login:
        room = message['room']

        if not server.database.room_exists(room):
            ## Room doesn't exist
            response = json.dumps({'type': 'pending_room',
                                'status': 'error',
                                'reason': 'room_does_not_exist'})
        elif room not in client.rooms:
            client.pending_rooms.append(room)
            server.database.execute_sql_query("UPDATE users SET pending_rooms = ? WHERE name = ?",
                                                    (','.join(client.pending_rooms), client.name,))
            response = json.dumps({'type': 'pending_room',
                                'status': 'ok'})
            
        else:
            ## 'Client' already in room
            response = json.dumps({'type': 'pending_room',
                                'status': 'error',
                                'reason': 'already_in_room'})

        ## Send response
        client.send(response.encode())
    else:
        ## If client is not logged in, send an error response
        response = json.dumps({'type': 'pending_room',
                            'status': 'error',
                            'reason': 'not_logged_in'})
        client.send(response)

################################################################################################################

def handle_public_message(message:dict, clients:list, client:'Client', server:'Server'):
    """
    Handle public message from the client.

    Args:
        message (dict): The public message.
        clients (list): The list of all clients.
        client ('Client'): The client.
        server ('Server'): The server.
    """
    if client.login:
        ## Check if the client is valid
        if client.state != "valid":
            ## If not, send an error response
            response = json.dumps({'type': 'public',
                                'status': 'error',
                                'reason': 'not_valid_sender'})
            client.send(response)
        else:
            ## If valid, extract message details and insert into the database
            message_text = message['message']
            ip = client.addr
            date_message = datetime.datetime.now()
            room = client.rooms

            try:
                server.database.insert_message(client.name, room, date_message, ip, message_text)
                response = json.dumps({'type': 'public',
                                    'room': room,
                                    'user': client.name,
                                    'message': message_text})
                ## Send the message to all valid clients in the room
                for cl in clients:
                    if room in cl.rooms and cl.state == "valid":
                        cl.send(response)
            except Exception as e:
                ## Handle any errors during message insertion
                response = json.dumps({'type': 'public',
                                    'status': 'error',
                                    'reason': str(e)})
                client.send(response)
    else:
        ## If client is not logged in, send an error response
        response = json.dumps({'type': 'public',
                            'status': 'error',
                            'reason': 'not_logged_in'})
        client.send(response)

################################################################################################################

def handle_private_message(message:dict, clients:list, client:'Client', server:'Server'):
    """
    Handle private message from the client.

    Args:
        message (dict): The private message.
        clients (list): The list of all clients.
        client ('Client'): The client.
        server ('Server'): The server.
    """
    if client.login:
        ## Find the recipient client
        to_user = None
        for cl in clients:
            if cl.name == message['to']:
                to_user = cl
                break

        ## If recipient found
        if to_user is not None:
            ## Check if sender is valid
            if client.state != "valid":
                response = json.dumps({'type': 'private',
                                    'status': 'error',
                                    'reason': 'not_valid_sender'})
                client.send(response)
            else:
                ## Extract message details
                message_text = message['message']
                ip = client.address
                date_message = datetime.datetime.now()
                room = ''.join(sorted([client.name, to_user.name]))

                ## If room doesn't exist, create it
                if not server.database.room_exists(room):
                    client.rooms = room
                    to_user.rooms = room
                    try:
                        server.database.execute_sql_query("INSERT INTO rooms (name) VALUES (?)",
                                                        (room,))
                    except Exception as e:
                        response = json.dumps({'type': 'private',
                                            'status': 'error',
                                            'reason': str(e)})
                        client.send(response)
                        return

                ## If recipient is valid, send the message
                if to_user.state == "valid":
                    try:
                        server.database.insert_message(client.name, room, date_message, ip, message_text)
                        response = json.dumps({'type': 'private',
                                            'room': room,
                                            'user': client.name,
                                            'message': message_text})
                        to_user.send(response)
                    except Exception as e:
                        response = json.dumps({'type': 'private',
                                            'status': 'error',
                                            'reason': str(e)})
                        client.send(response)
                else:
                    response = json.dumps({'type': 'private',
                                        'status': 'error',
                                        'reason': 'recipient_is_not_valid'})
                    client.send(response)
        else:
            ## If recipient not found, send an error response
            response = json.dumps({'type': 'private',
                                'status': 'error',
                                'reason': 'recipient_not_found'})
            client.send(response)
    else:
        ## If sender is not logged in, send an error response
        response = json.dumps({'type': 'private',
                            'status': 'error',
                            'reason': 'not_logged_in'})
        client.send(response)
