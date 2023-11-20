"""
Ce module est le point d'entrée pour l'application serveur.

Il analyse les arguments de la ligne de commande pour l'hôte et le port, les valide, puis démarre le serveur.

Fonctions
---------
server(host: str, port: int) -> None
    Démarre le serveur avec l'hôte et le port donnés.

Lève
------
ValueError
    Si le port n'est pas un entier entre 0 et 65535, ou si les arguments de la ligne de commande ne sont pas fournis.
getopt.GetoptError
    Si les arguments de la ligne de commande ne sont pas dans le bon format.

Exemples
--------
Pour démarrer le serveur avec l'hôte 127.0.0.1 et le port 5000, exécutez la commande suivante :

    python main.py -a 127.0.0.1 -p 5000
"""

from backend.server.server import server
from backend.database import connexion_mysql
import sys, getopt

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:p:", ["host=", "port="])
        if not args:
            raise ValueError
    except ValueError:
        print("main.py -a <address> -p <port>")
        sys.exit(2)
    except getopt.GetoptError:
        print("main.py -a <address> -p <port>")
        sys.exit(2)

    try:
        host = args[0]
        port = int(args[1])
        if port not in range(0, 65536):
            raise ValueError("Le port doit être un entier entre 0 et 65535")
    except ValueError as err:
        print(err)
    else:
        connexion_mysql()
        server(host, port)
   