import json, datetime, bcrypt
from .client import Client
from .server import Server

###############################################################################################

def handle_inscription_message(message:json, client:Client, server:Server):
    user = message['user']
    password = message['password'].encode('utf-8')

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)

    result = server.database.fetch_one("SELECT name FROM users WHERE name = %s",
                                       (user,))
    if len(result) == 0:
        client.name = user

        creation_date = datetime.datetime.now()
        server.database.execute_sql_query("INSERT INTO users (name, password, date_creation) VALUES (%s, %s, %s)",
                                          (user, hashed_password, creation_date))

        response = json.dumps({'type': 'inscription',
                               'status': 'ok'})
        client.send(response)

    else:
        response = json.dumps({'type': 'inscription',
                               'status': 'ko',
                               'reason': 'already_used'})
        client.send(response)

###############################################################################################

def handle_connexion_message(message:json, client:Client, server:Server):
    user = message['user']
    password = message['password'].encode('utf-8')

    result = server.database.fetch_one("SELECT name FROM users WHERE name = %s",
                                       (user,))
    if len(result) > 0: 
        result = server.database.fetch_one("SELECT password FROM users WHERE name = %s",
                                           (user,))
        hashed_password = result[0][0].encode('utf-8')

        if not bcrypt.checkpw(password, hashed_password): 
            response = json.dumps({'type': 'connexion',
                                   'status': 'ko',
                                   'reason': 'incorrect_password'})
            client.send(response)
        
        else:
            client.name = user
            client.state = server.database.fetch_user_state(user)
                     
            result = server.database.fetch_one("SELECT room FROM rooms, users WHERE users.name = %s",
                                               (user,))
            client.salon = result if result else None

            if client.state == "valid":
                response = json.dumps({'type': 'connexion',
                                       'status': 'ok'})
                client.send(response)
                                  
            elif client.state == "kick":
                result = server.database.fetch_one("SELECT timeout FROM users WHERE name = %s",
                                                   (user,))
                timeout = result[0][0] if result else None

                result = server.database.fetch_one("SELECT reason FROM users WHERE name = %s",
                                                   (user,))
                reason = result[0][0] if result else None

                response = json.dumps({'type': 'connexion',
                                       'status': 'kick',
                                       'timeout': timeout,
                                       'reason': reason})
                client.send(response)
                                     
            elif client.state == "ban":
                result = server.database.fetch_one("SELECT reason FROM users WHERE name = %s",
                                                   (user,))
                reason = result[0][0] if result else None

                response = json.dumps({'type': 'connexion',
                                       'status': 'ban',
                                       'reason': reason})
                client.send(response)
    
    else:
        response = json.dumps({'type': 'connexion',
                               'status': 'ko',
                               'reason': 'incorrect_username'})
        client.send(response)

#################################rejvkbejkrhbvehk##############################################################

def handle_demande_salon_message(message:json, client:Client, server:Server):
    salon = message['salon']

    result = server.database.fetch_one("SELECT nom FROM salons WHERE nom = %s", (salon,))
    if len(result) == 0:
        server.database.execute_sql_query("INSERT INTO salons (nom) VALUES (%s)", (salon,))
        client.salon = salon

        response = json.dumps({'type': 'demande_salon', 'status': 'ok'})
        client.envoyer(response.encode())

    else:
        result = server.database.fetch_all("SELECT nom, nom FROM salons, utilisateurs WHERE utilisateurs.nom = %s AND salons.nom = %s", (client.nom, salon,))

        if len(result) == 0:
            client.salon = salon
            server.database.execute_sql_query("UPDATE utilisateurs SET salon = %s WHERE nom = %s", (client.salon, client.nom,))

            response = json.dumps({'type': 'demande_salon','status': 'ok'})
            client.envoyer(response.encode())

        else:
            response = json.dumps({'type': 'demande_salon', 'status': 'ko', 'raison': 'already_in_salon'})
            client.envoyer(response.encode())

###############################################################################################

def handle_text_message(message:json, clients:list, client:Client, server:Server):
    if client.etat == "kick":
        result = server.database.fetch_one("SELECT timeout FROM utilisateurs WHERE nom = %s", (client.nom,))
        timeout = result[0][0] if result else None

        result = server.database.fetch_one("SELECT raison FROM utilisateurs WHERE nom = %s", (client.nom,))
        raison = result[0][0] if result else None

        response = json.dumps({'type': 'connexion', 'status': 'kick', 'timeout': timeout, 'raison': raison})

    elif client.etat == "ban":
        result = server.database.fetch_one("SELECT raison FROM utilisateurs WHERE nom = %s", (client.nom,))
        raison = result[0][0] if result else None

        response = json.dumps({'type': 'connexion', 'status': 'ban', 'raison': raison})

    else:
        salon = message['salon']
        message = message['message']
        ip = client.addr
        date_message = datetime.datetime.now()

        server.database.execute_sql_query("INSERT INTO messages (user, salon, date_message, ip, body) VALUES (%s, %s, %s, %s, %s)", (client.nom, salon, date_message, ip, message,))

        for cl in clients:
            if cl.salon == salon and cl != client:
                response = json.dumps({'type': 'text', 'user': client.nom, 'message': message})
                cl.envoyer(response)

###############################################################################################

def handle_private_message(message:json, clients:list, client:Client, server:Server):
    to_user = None
    for cl in clients:
        if cl.nom == message['to']:
            to_user = cl
            break

    try:
        if to_user is not None:
            if client.etat != "valid":
                response = json.dumps({'type': 'not_valid_sender', 'status': client.etat})
                client.envoyer(response)

            else:
                result = server.database.fetch_one("SELECT nom FROM utilisateurs WHERE nom = %s", (to_user.nom,))
                if len(result) > 0:
                    message = message['message']
                    ip = client.addr
                    date_message = datetime.datetime.now()
                    salon = ''.join(sorted([client.nom, to_user.nom]))

                    result = server.database.fetch_one("SELECT nom FROM salons WHERE nom = %s", (salon,))
                    if len(result) == 0:
                        client.salon = salon
                        to_user.salon = salon
                        server.database.execute_sql_query("INSERT INTO salons (nom) VALUES (%s)", (salon,))
                        server.database.connection.commit()

                    if to_user.etat == "valid":
                        server.database.execute_sql_query("INSERT INTO messages (user, salon, date_message, ip, body) VALUES (%s, %s, %s, %s, %s)", (client.nom, salon, date_message, ip, message,))
                        response = json.dumps({'type': 'text', 'user': client.nom, 'message': message})
                        to_user.envoyer(response)

                    else:
                        response = json.dumps({'type': 'private', 'status': to_user.etat, 'raison': 'user_not_valid'})
                        client.envoyer(response)

                else:
                    response = json.dumps({'type': 'private', 'status': 'ko', 'raison': 'user_not_found'})
                    client.envoyer(response)

    except NameError:
        response = json.dumps({'type': 'private', 'status': 'ko', 'raison': 'user_not_found'})
        client.envoyer(response)

