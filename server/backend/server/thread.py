import json, datetime, bcrypt
from classes import Client
from .. import database

def handler(client:Client, clients:list) -> None:
    global flag, flag2
    while not flag2:
        try:
            data = client.receive()
            message = json.loads(data)

            ## Si le message est une demande d'inscription
            if message['type'] == 'inscription':
                user = message['user']
                mdp = message['hash_mdp'].encode('utf-8')
                demande = message['demande']

                ## Hash le mot de passe
                salt = bcrypt.gensalt()
                hash_mdp = bcrypt.hashpw(mdp, salt)

                database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s", (user))
                
                ## Si le nom n'est pas déjà utilisé
                if database.cursor.rowcount == 0:
                    client.nom = user

                    creation = datetime.datetime.now()
                    database.cursor.execute("INSERT INTO utilisateurs (nom, mdp, demande, date_creation) VALUES (%s, %s, %s, %s)", 
                                            (user, hash_mdp, demande, creation))
                    
                    database.connection.commit()

                    response = json.dumps({'type': 'inscription', 
                                        'status': 'ok'})
                    client.envoyer(response.encode())
                    
                ## Si le nom est déjà utilisé
                else:
                    response = json.dumps({'type': 'inscription',
                                        'status': 'ko',
                                        'raison': 'nom déjà utilisé'})
                    client.envoyer(response.encode())
                
                database.connection.close()

            ## Si le message est une demande de connexion
            if message['type'] == 'connexion':
                user = message['user']
                mdp = message['hash_mdp'].encode('utf-8')

                database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s)", (user))
                
                ## Si le nom existe
                if database.cursor.rowcount > 0:
                    database.cursor.execute("SELECT mdp FROM utilisateurs WHERE nom = %s", (user))
                    hash_mdp = database.cursor.fetchone()
                    if not bcrypt.checkpw(mdp, hash_mdp):
                        response = json.dumps({'type': 'connexion', 
                                            'status': 'ko',
                                            'raison': 'incorrect_password'})
                        client.envoyer(response.encode())
                    else:
                        client.nom = user

                        ## Récupère l'état de l'utilisateur
                        database.cursor.execute("SELECT etat FROM utilisateurs WHERE nom = %s", (user))
                        client.etat = database.cursor.fetchone()
                        
                        ## Récupère les salons de l'utilisateur
                        database.cursor.execute("SELECT salon FROM salons, utilisateurs WHERE utilisateur.nom = %s", (user))
                        salon = database.cursor.fetchall()

                        ## Si l'état de l'utilisateur est "valid"
                        if client.etat == "valid":
                            response = json.dumps({'type': 'connexion',
                                                'status': 'ok'})
                            client.envoyer(response.encode())
                        
                        ## Si l'état de l'utilisateur est "kick"
                        elif client.etat == "kick":
                            database.cursor.execute("SELECT timeout FROM utilisateurs WHERE nom = %s", (user))
                            timeout = database.cursor.fetchone()

                            database.cursor.execute("SELECT raison FROM utilisateurs WHERE nom = %s", (user))
                            raison = database.cursor.fetchone()

                            response = json.dumps({'type': 'connexion',
                                                'status': 'kick',
                                                'timeout': timeout,
                                                'raison': raison})
                        
                        ## Si l'état de l'utilisateur est "ban"
                        elif client.etat == "ban":
                            database.cursor.execute("SELECT raison FROM utilisateurs WHERE nom = %s", (user))
                            raison = database.cursor.fetchone()

                            response = json.dumps({'type': 'connexion',
                                                'status': 'ban',
                                                'raison': raison})
                
                ## Si le nom n'existe pas 
                else:
                    response = json.dumps({'type': 'connexion', 
                                        'status': 'ko',
                                        'raison': 'incorrect_username'})

                    client.envoyer(response.encode())
                
                database.connection.close()

            ## Si le message est un message de salon
            elif message['type'] == 'text':
                if client.etat() != "valid":
                    response = json.dumps({'type': 'not_valid_sender', 
                                        'status': user.etat()})
                    client.envoyer(response.encode())

                else:
                    salon = message['salon']
                    message = message['message']


                    ip = client.addr()
                    date_message = datetime.datetime.now()

                    ## Stock le message dans la base de données
                    database.cursor.execute("INSERT INTO messages (user, salon, date_message, ip, body) VALUES (%s, %s, %s, %s, %s)",
                                            (user.nom(), salon, date_message, ip, message))
                    database.connection.commit()
                    
                    for cl in clients:
                        if cl != client:
                            
                            ## Envoie le messages aux autres utilisateurs du salons dont leur état est "valid"
                            if cl.etat() == "valid" and salon in cl.salon():
                                cl.envoyer(data.encode())
                    
                    database.connection.close()
            
            ## Si le message est un message privé
            elif message['type'] == 'private':
                to_user = Client(message['to_user'])

                if client.etat() != "valid":
                    response = json.dumps({'type': 'not_valid_sender', 
                                        'status': user.etat()})
                    client.envoyer(response.encode())

                else:
                    database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s", (to_user))
                    if database.cursor.rowcount > 0:
                        message = message['message']

                        ip = client.addr()
                        date_message = datetime.datetime.now()

                        salon1 = user + to_user
                        salon2 = to_user + user
                        
                        ## Créer un salon privé si il n'existe pas
                        database.cursor.execute("SELECT nom FROM salons WHERE nom = %s", (salon1))
                        if database.cursor.rowcount == 0:
                            database.cursor.execute("SELECT nom FROM salons WHERE nom = %s", (salon2))
                            if database.cursor.rowcount == 0:
                                client.salon(salon1)
                                to_user.salon(salon1)
                                database.cursor.execute("INSERT INTO salons (nom) VALUES (%s)", (salon1))
                                database.connection.commit()
                            else:
                                salon = salon2
                        else:
                            salon = salon1
                    
                        if to_user.etat() == "valid":
                            ## Stock le message dans la base de données
                            database.cursor.execute("INSERT INTO messages (user, salon, date_message, ip, body) VALUES (%s, %s, %s, %s, %s)",
                                                (client.nom(), salon, date_message, ip, message))
                            database.connection.commit()

                            ## Envoie le message à l'utilisateur
                            to_user.envoyer(data.encode())

                        else:
                            response = json.dumps({'type': 'not_valid_receiver', 
                                                'status': to_user.etat()})
                            client.envoyer(response.encode())

                        database.connection.close()

        except(ConnectionResetError):
            print("Connexion réinitialisée")
        except(BrokenPipeError):
            print("Rupture de la connexion")
