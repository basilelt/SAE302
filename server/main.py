from .server.server import Server
import argparse, sys

def main():
    parser = argparse.ArgumentParser(description='Python chat server.')
    parser.add_argument('-a', '--host', type=str, required=True, help='Host address')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port number')

    args = parser.parse_args()

    host = args.host
    port = args.port

    if port not in range(0, 65536):
        print("Port must be an integer between 0 and 65535")
        sys.exit(2)

    server = Server(host, port)
    server.run()

if __name__ == "__main__":
    main()