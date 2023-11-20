"""
Ce module est le point d'entrée pour l'application client.

Il analyse les arguments de la ligne de commande pour l'hôte et le port, les valide, puis démarre le client.

Fonctions
---------
client(user:str, host: str, port: int) -> None
    Démarre le client avec l'hôte et le port donnés.

Lève
------
ValueError
    Si le port n'est pas un entier entre 0 et 65535.
getopt.GetoptError
    Si les arguments de la ligne de commande ne sont pas dans le bon format.

Exemples
--------
Pour démarrer le client avec l'hôte 127.0.0.1 et le port 5000, exécutez la commande suivante :

    python main.py -u fred -p 5000 -a 127.0.0.1
"""

from backend.client import client
import sys, getopt

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:a:p:", ["user=", "host=", "port="])
        if not args or len(args) != 3:
            raise ValueError
    except ValueError:
        print("main.py -u <user> -p <port> -a <address>")
        sys.exit(2)
    except getopt.GetoptError:
        print("main.py -u <user> -p <port> -a <address>")
        sys.exit(2)

    try:
        user = args[0]
        host = args[1]
        port = int(args[2])
        if port not in range(0, 65536):
            raise ValueError("Le port doit être un entier entre 0 et 65535")
    except ValueError as err:
        print(err)
    else:
        client(user, host, port)
