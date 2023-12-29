import argparse
import sys
import logging
import threading
from server.server import Server
from server.admin import admin_console, admin_cmd

def main():
    """
    Main function to start the chat server.
    Parses command line arguments for host and port, validates them, and starts the server.
    """

    ## Configure logging
    logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

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
        
        server_thread = threading.Thread(target=server.run)
        console_thread = threading.Thread(target=admin_console, args=(server,))
        admin_thread = threading.Thread(target=admin_cmd, args=(server,))

        server_thread.start()
        console_thread.start()
        admin_thread.start()

    except KeyboardInterrupt:
        ## Handle keyboard interrupt
        print(f"\nServer is shutting down...")
        server.close()
        
        ## Wait for threads to finish
        server_thread.join()
        console_thread.join()
        admin_thread.join()
        
        print("Server has shut down.")
    except Exception as e:
        print(f"Failed to run the server: {e}")
        logging.error(f"Failed to run the server: {e}")
    finally:
        server_thread.join()
        console_thread.join()
        admin_thread.join()


if __name__ == "__main__":
    main()
