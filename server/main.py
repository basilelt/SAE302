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
   