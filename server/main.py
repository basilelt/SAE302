import argparse
import sys
import logging
from .server.server import Server

def main():
    """
    Main function to start the chat server.
    Parses command line arguments for host and port, validates them, and starts the server.
    """

    ## Configure logging
    logging.basicConfig(filename='server.log', level=logging.INFO)

    parser = argparse.ArgumentParser(description='Python chat server.')
    parser.add_argument('-a', '--host', type=str, required=True, help='Host address')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port number')

    args = parser.parse_args()
    host = args.host
    port = args.port

    ## Validate port number
    if port not in range(0, 65536):
        logging.error("Port must be an integer between 0 and 65535")
        sys.exit(2)

    ## Start the server
    try:
        server = Server(host, port)
        server.run()
    except Exception as e:
        logging.error(f"Failed to run the server: {e}")

if __name__ == "__main__":
    main()
