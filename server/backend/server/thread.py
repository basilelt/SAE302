import json, datetime
from classes import Client
from .. import database

def handler(client:Client, clients) -> None:
    global flag, flag2
    while not flag2:
        try:
            data = client.conn().recv(1024).decode()
            message = json.loads(data)

            if message['type'] == 'inscription':
                user = message['user']
                hash_mdp = message['hash_mdp']
                demande = message['demande']

                database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s", (user))
                if database.cursor.rowcount == 0:
                    client.nom = user

                    creation = datetime.datetime.now()
                    database.cursor.execute("INSERT INTO utilisateurs (nom, mdp, demande, date_creation) VALUES (%s, %s, %s, %s)", 
                                            (user, hash_mdp, demande, creation))
                    
                    database.connection.commit()

                    response = json.dumps({'type': 'inscription', 
                                        'status': 'ok'})
                    client.conn().send(response.encode())
                    
                    
                else:
                    response = json.dumps({'type': 'inscription',
                                        'status': 'ko',
                                        'raison': 'nom déjà utilisé'})
                    client.conn().send(response.encode())
                
                database.connection.close()

            if message['type'] == 'connexion':
                user = message['user']
                hash_mdp = message['hash_mdp']

                database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s AND mdp = %s", (user, hash_mdp))
                if database.cursor.rowcount > 0:
                    client.nom = user

                    database.cursor.execute("SELECT etat FROM utilisateurs WHERE nom = %s", (user))
                    client.etat = database.cursor.fetchone()

                    database.cursor.execute("SELECT salon FROM salons, utilisateurs WHERE utilisateur.nom = %s", (user))
                    salon = database.cursor.fetchall()

                    if client.etat == "valid":
                        response = json.dumps({'type': 'connexion',
                                            'status': 'ok'})
                        client.conn().send(response.encode())
                    
                    elif client.etat == "kick":
                        database.cursor.execute("SELECT timeout FROM utilisateurs WHERE nom = %s", (user))
                        timeout = database.cursor.fetchone()

                        database.cursor.execute("SELECT raison FROM utilisateurs WHERE nom = %s", (user))
                        raison = database.cursor.fetchone()

                        response = json.dumps({'type': 'connexion',
                                            'status': 'kick',
                                            'timeout': timeout,
                                            'raison': raison})
                    
                    elif client.etat == "ban":
                        database.cursor.execute("SELECT raison FROM utilisateurs WHERE nom = %s", (user))
                        raison = database.cursor.fetchone()

                        response = json.dumps({'type': 'connexion',
                                            'status': 'ban',
                                            'raison': raison})
                    
                else:
                    response = json.dumps({'type': 'connexion', 
                                        'status': 'ko'})
                    client.conn().envoyer(response.encode())
                
                database.connection.close()
      
            elif message['type'] == 'text':
                user = Client(message['user'])
                salon = message['salon']
                message = message['message']

                ip = client.addr()
                date_message = datetime.datetime.now()

                database.cursor.execute("INSERT INTO messages (user, salon, date_message, ip, body) VALUES (%s, %s, %s, %s, %s)",
                                        (user.nom(), salon, date_message, ip, message))
                database.connection.commit()
                
                for cl in clients:
                    if cl != client:
                        if cl.etat() == "valid" and salon in cl.salon():
                            cl.envoyer(data.encode())
                
                database.connection.close()
            
            elif message['type'] == 'private':
                user = Client(message['user'])
                to_user = Client(message['to_user'])

                database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s", (to_user))
                if database.cursor.rowcount > 0:
                    message = message['message']

                    ip = client.addr()
                    date_message = datetime.datetime.now()

                    salon1 = user + to_user
                    salon2 = to_user + user

                    database.cursor.execute("SELECT nom FROM salons WHERE nom = %s", (salon1))
                    if database.cursor.rowcount == 0:
                        database.cursor.execute("SELECT nom FROM salons WHERE nom = %s", (salon2))
                        if database.cursor.rowcount == 0:
                            user.salon(salon1)
                            to_user.salon(salon1)
                            database.cursor.execute("INSERT INTO salons (nom) VALUES (%s)", (salon1))
                            database.connection.commit()
                        else:
                            salon = salon2
                    else:
                        salon = salon1
                
                    if to_user.etat() == "valid":
                        database.cursor.execute("INSERT INTO messages (user, salon, date_message, ip, body) VALUES (%s, %s, %s, %s, %s)",
                                             (user, salon, date_message, ip, message))
                        database.connection.commit()
                        to_user.envoyer(data.encode())
                    
                    database.connection.close()
 
        except(ConnectionResetError):
            print("Connexion réinitialisée")
        except(BrokenPipeError):
            print("Rupture de la connexion")
