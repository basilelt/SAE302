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

def convert_to_date_minus(time_str:str) -> datetime:
    """
    Convert a string to a datetime object.

    Args:
        time_str (str): The string to convert.
    """
    number = int(time_str[:-1])
    unit = time_str[-1]

    if unit == 's':
        return datetime.now() - timedelta(seconds=number)
    elif unit == 'm':
        return datetime.now() - timedelta(minutes=number)
    elif unit == 'h':
        return datetime.now() - timedelta(hours=number)
    elif unit == 'd':
        return datetime.now() - timedelta(days=number)
    elif unit == 'y':
        return datetime.now() - timedelta(days=number*365)
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
            print("")
            print("messages <time> - display a list of all messages since a time")
            print("users - display a list of all users")
            print("")
            print("rooms - display a list of all rooms")
            print("add room <room1,room2,...> - add a room")
            print("pending rooms <username> - display a list of pending rooms for a user")
            print("accept pending <username> <room1,room2,...> - accept pending rooms for a user")
            print("")
            print("kick <username> <timeout> <reason> - kick a user")
            print("unkick <username> - unkick a user")
            print("")
            print("ban <username> <reason> - ban a user")
            print("ban ip <ip> <reason> - ban an IP address")
            print("unban <username> - unban a user")
            print("unban ip <ip> - unban an IP address")
            print("")
            print("shutdown - shutdown the server")

        ########################################################################################################

        elif command.startswith("messages"):
            try:
                date = convert_to_date_minus(command.split(" ")[1])
                print(f"Messages since {date}:")
                for message in server.messages:
                    if message.date >= date:
                        print(message)
            except IndexError:
                print("Please specify a date")
        
        elif command == "users":
            print("Users:")
            for user in server.clients:
                print(user.name + " " + user.ip)
        
        elif command == "rooms":    
            print("Rooms:")
            for room in server.rooms:
                print(room)
        
        elif command.startswith("add room"):
            try:
                rooms = command.split(" ")[2]
                for room in rooms.split(","):
                    server.addroom(room)
            except IndexError:
                print("Please specify a room")
        
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

        ########################################################################################################

        elif command.startswith("kick"):
            if command.split(" ")[1] == "ip":
                try:
                    ip = command.split(" ")[2]
                    timeout = convert_to_date(command.split(" ")[3])
                    reason = " ".join(command.split(" ")[4:])
                    server.kick_ip(ip, timeout, reason)
                except IndexError:
                    print("Please specify an IP address")
            else:
                try:
                    username = command.split(" ")[1]
                    timeout = convert_to_date(command.split(" ")[2])
                    reason = " ".join(command.split(" ")[3:])
                    server.kick_user(username, timeout, reason)
                except IndexError:
                    print("Please specify a username")
        
        elif command.startswith("unkick"):
            if command.split(" ")[1] == "ip":
                try:
                    ip = command.split(" ")[2]
                    server.unkick_ip(ip)
                except IndexError:
                    print("Please specify an IP address")
            else:
                try:
                    username = command.split(" ")[1]
                    server.unkick_user(username)
                except IndexError:
                    print("Please specify a username")

        ########################################################################################################
        
        elif command.startswith("ban"):
            if command.split(" ")[1] == "ip":
                try:
                    ip = command.split(" ")[2]
                    reason = " ".join(command.split(" ")[3:])
                    server.ban_ip(ip, reason)
                except IndexError:
                    print("Please specify an IP address")
            else:
                try:
                    username = command.split(" ")[1]
                    reason = " ".join(command.split(" ")[2:])
                    server.ban_user(username, reason)
                except IndexError:
                    print("Please specify a username")
        
        elif command.startswith("unban"):
            if command.split(" ")[1] == "ip":
                try:
                    ip = command.split(" ")[2]
                    server.unban_ip(ip)
                except IndexError:
                    print("Please specify an IP address")
            else:
                try:
                    username = command.split(" ")[1]
                    server.unban_user(username)
                except IndexError:
                    print("Please specify a username")

        ########################################################################################################
        
        elif command.startswith("kill"):
            user = command.split(" ")[1]
            reason = command.split(" ")[2:]
            server.kill(user, reason)
            print(f"Killed {user}")

        elif command == "shutdown":
            print("Server is shutting down...")
            server.close()
            print("Server has shut down.")
        else:
            print("Invalid command. Type 'help' for a list of commands.")
