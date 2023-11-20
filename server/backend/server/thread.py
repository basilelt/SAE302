import re
from classes import Client
import database

def handler(client:Client, clients) -> None:
    global flag, flag2
    while not flag2:
        try:
            data = client.conn().recv(1024).decode()

            pattern_bonjour = r'packet_bonjour:.*,.*'
            match_bonjour = re.search(pattern_bonjour, data)

            pattern_bye = r'packet_bye:.*,.*'
            match_bonjour = re.search(pattern_bonjour, data)

            if match_bonjour:
                bonjour = data.split(":")[1]
                user = bonjour.split(",")[0]
                hash_mdp = bonjour.split(",")[1]
                
                database.cursor.execute("SELECT * FROM utilisateurs WHERE nom = %s AND mdp = %s", (user, hash_mdp))
                if database.cursor.rowcount > 0:
                    client.conn().send("packet_bonjour:ok".encode())
                    client.nom = user
                else:
                    client.conn().send("packet_bonjour:ko".encode())

                    
            elif data:
                database.cursor.execute("INSERT INTO prise_selected_plage (prise_id, plage_id) VALUES (%s, %s)", (id, plage_id))
                for cl in clients:
                    if cl != client:
                        cl.envoyer(data.encode())

        except(ConnectionResetError):
            print("Connexion réinitialisée")
        except(BrokenPipeError):
            print("Rupture de la connexion")
