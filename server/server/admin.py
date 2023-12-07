from datetime import datetime, timedelta

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .server import Server

def convert_to_date(time_str:str) -> datetime:
    """
    Convert a string to a datetime object.

    Args:
        time_str (str): The string to convert.
    """
    number = int(time_str[:-1])
    unit = time_str[-1]

    if unit == 's':
        return datetime.now() + timedelta(seconds=number)
    elif unit == 'm':
        return datetime.now() + timedelta(minutes=number)
    elif unit == 'h':
        return datetime.now() + timedelta(hours=number)
    elif unit == 'd':
        return datetime.now() + timedelta(days=number)
    elif unit == 'y':
        return datetime.now() + timedelta(days=number*365)
    else:
        raise ValueError("Invalid time unit. Use 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days, or 'y' for years.")

################################################################################################################

def admin_console(server:'Server'):
    """
    Display the admin console.

    Args:
        server ('Server'): The server.
    """
    print("Admin console")
    print("Type 'help' for a list of commands.")
    

def admin_cmd(server:'Server'):
    """
    Admin commands to manage the server.

    Args:
        server ('Server'): The server.
    """
    while not server.stop_server:
        command = input()
        if command == "help":
            print("Available commands:")
            print("help - display this help message")
            print("users - display a list of all users")
            print("rooms - display a list of all rooms")
            print("pending rooms <username> - display a list of pending rooms for a user")
            print("accept pending <username> <room1,room2,...> - accept pending rooms for a user")
            print("kick <username> <timeout> <reason> - kick a user")
            print("ban <username> <reason> - ban a user")
            print("shutdown - shutdown the server")
        elif command == "help kick":
            print("kick <username> <timeout> <reason> - kick a user")
            print("timeout - 2d, 3h, 5m, etc.")
        elif command == "users":
            print("Users:")
            for user in server.clients:
                print(user.name)
        elif command == "rooms":    
            print("Rooms:")
            for room in server.rooms:
                print(room)
        elif command.startswith("pending rooms"):
            try:
                username = command.split(" ")[2]
                print(f"Pending rooms for {username}:")
                for client in server.clients:
                    if client.name == username:
                        for room in client.pending_rooms:
                            print(room)
                        break
            except IndexError:
                print("Please specify a username")
        elif command.startswith("accept pending"):
            try:
                username = command.split(" ")[2]
                rooms = command.split(" ")[3]
                if rooms == "all":
                    for client in server.clients:
                        if client.name == username:
                            for room in client.pending_rooms:
                                client.addroom(server, room) 
                            break
                else:
                    for room in rooms.split(","):
                        for client in server.clients:
                            if client.name == username:
                                client.addroom(server, room)
                                break
            except IndexError:
                print("Please specify a username and a room")

        elif command.startswith("kick"):
            try:
                username = command.split(" ")[1]
                timeout = convert_to_date(command.split(" ")[2])
                reason = " ".join(command.split(" ")[3:])
                server.kick_user(username, timeout, reason)
            except IndexError:
                print("Please specify a username")
        elif command.startswith("unkick"):
            try:
                username = command.split(" ")[1]
                server.unkick_user(username)
            except IndexError:
                print("Please specify a username")
        elif command.startswith("ban"):
            try:
                username = command.split(" ")[1]
                reason = " ".join(command.split(" ")[2:])
                server.ban_user(username, reason)
            except IndexError:
                print("Please specify a username")
        elif command.startswith("unban"):
            try:
                username = command.split(" ")[1]
                server.unban_user(username)
            except IndexError:
                print("Please specify a username")
        elif command == "shutdown":
            print("Server is shutting down...")
            server.close()
            print("Server has shut down.")
        else:
            print("Invalid command. Type 'help' for a list of commands.")
