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
            server.database.execute_sql_query("INSERT INTO users (name, password, ip, date_creation) VALUES (:name, :password, :ip, :date_creation)",
                                              {'name':user,
                                               'password':hashed_password,
                                               'ip':client.ip[0],
                                               'date_creation':creation_date})
            client.login = True
            client.state = "valid"
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
            server.database.execute_sql_query("UPDATE users SET ip = :ip WHERE name = :name",
                                              {'ip':client.ip[0],
                                               'name':user})
                     
            result = server.database.fetch_all("SELECT room FROM belong WHERE user = :name",
                                               {'name': user})
            client.rooms = [row[0] for row in result] if result else []

            result = server.database.fetch_all("SELECT pending_rooms FROM users WHERE users.name = :name",
                                               {'name':user})
            list_result = result[0][0].split(',') if result[0][0] is not None else []
            client.pending_rooms = list_result
             
            if client.state == "valid":
                ## Valid user
                response = json.dumps({'type': 'signin',
                                       'status': 'ok',
                                       'all_rooms': server.database.get_rooms(),
                                       'rooms': client.rooms,})
                client.login = True
                client.send(response)
                                  
            elif client.state == "kick" or client.state == "kick_ip":
                ## Kicked user
                result = server.database.fetch_one("SELECT timeout FROM users WHERE name = :name",
                                                   {'name':user})
                timeout = result[0] if result else None
                if datetime.datetime.now() > timeout:
                    ## If timeout has expired, unkick the user
                    server.database.execute_sql_query("UPDATE users SET state = 'valid' WHERE name = :name",
                                                      {'name':user})
                    client.state = "valid"
                    response = json.dumps({'type': 'signin',
                                           'status': 'ok',
                                           'all_rooms': server.database.get_rooms(),
                                           'rooms': client.rooms,})
                    client.login = True
                    client.send(response)
                else:
                    ## If timeout has not expired, send a kick status response
                    result = server.database.fetch_one("SELECT reason FROM users WHERE name = :name",
                                                    {'name':user})
                    reason = result[0] if result else None

                    response = json.dumps({'type': 'signin',
                                        'status': 'kick',
                                        'timeout': timeout.strftime("%Y-%m-%d %H:%M:%S"),
                                        'reason': reason})
                    client.send(response)
                    client.close(clients)
                                     
            elif client.state == "ban" or client.state == "ban_ip":
                ## Banned user
                result = server.database.fetch_one("SELECT reason FROM users WHERE name = :name",
                                                   {'name':user})
                reason = result[0] if result else None

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
        response = json.dumps({'type': 'disconnect',
                              'status': 'ok'})
        client.send(response)
        client.close(clients)
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
        elif room not in client.rooms and room is not None:
            client.pending_rooms.append(room)
            server.database.execute_sql_query("UPDATE users SET pending_rooms = :pending_rooms WHERE name = :name",
                                              {'pending_rooms':','.join(client.pending_rooms),
                                               'name':client.name,})
            response = None
            
        else:
            ## 'Client' already in room
            response = json.dumps({'type': 'pending_room',
                                   'status': 'error',
                                   'reason': 'already_in_room'})

        ## Send response
        if response:
            client.send(response)
    else:
        ## If client is not logged in, send an error response
        response = json.dumps({'type': 'pending_room',
                               'status': 'error',
                               'reason': 'not_logged_in'})
        client.send(response)

################################################################################################################

def handle_public_message(message:dict, client:'Client', clients:list, server:'Server'):
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
            date_message = datetime.datetime.now()
            room = message['room']

            try:
                server.database.insert_message(client.name, room, date_message, message_text)
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

def handle_private_message(message:dict, client:'Client', clients:list, server:'Server'):
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
                date_message = datetime.datetime.now()
                room = ''.join(sorted([client.name, to_user.name]))

                ## If room doesn't exist, create it
                if not server.database.room_exists(room):
                    try:
                        server.database.execute_sql_query("INSERT INTO rooms (name, type) VALUES (:name, :type)",
                                                          {'name': room,
                                                           'type': 'private'})
                        client.addroom(server, room)
                        to_user.addroom(server, room)
                    except Exception as e:
                        response = json.dumps({'type': 'private',
                                               'status': 'error',
                                               'reason': str(e)})
                        client.send(response)
                        return
                    
                ## Send a success response
                response = json.dumps({'type': 'private',
                                       'status': 'ok'})
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
