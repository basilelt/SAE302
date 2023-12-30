from datetime import datetime, timedelta
import logging

try:
    import readline
except ImportError:
    try:
        import pyreadline3 as readline ## readline is not available on Windows by default
    except ImportError:
        logging.error("Failed to import readline, please install it")
        print("Please install pyreadline on Windows")

## Import the types for documentation purposes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .server import Server

def convert_to_date(time_str:str) -> datetime:
    """
    Convert a string to a datetime object with a delta.

    :param str time_str: The string to convert.
    :return: The datetime object.
    :rtype: datetime
    :raises ValueError: If the time unit is not 's', 'm', 'h', 'd', or 'y'.
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
    Convert a string to a datetime object with a delta subtracted from the current time.

    :param str time_str: The string to convert.
    :return: The datetime object.
    :rtype: datetime
    :raises ValueError: If the time unit is not 's', 'm', 'h', 'd', or 'y'.
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

    :param Server server: The server.
    """
    print("Admin console")
    print("Type 'help' for a list of commands.")

def create_completer(server:'Server') -> 'function':
    """
    Creates a function that can be used as a completer for readline.

    :param Server server: The server instance. Used to get the list of clients for user-specific commands.
    :return: A function that takes the current text and a state and returns the next matching command.
    :rtype: function
    """
    base_commands = ["help", "messages", "users", "rooms", "add room", "pending rooms", "accept pending", "kick", "unkick", "ban", "unban", "kill", "shutdown"]
    user_commands = [f"{command} {user.name}" for command in ["kick", "unkick", "ban", "unban", "pending rooms", "accept pending"] for user in server.clients]
    ip_commands = [f"{command} ip" for command in ["ban", "unban"]]

    def completer(text:str, state:int) -> str or None:
        """
        Returns the next matching command.

        :param str text: The current text.
        :param int state: The state.
        :return: The next matching command.
        :rtype: str or None
        """
        line = readline.get_line_buffer().split()
        if not line:
            commands = base_commands
        else:
            first_word = line[0]
            if first_word in ["ban", "unban"]:
                commands = ip_commands + user_commands
            elif any(first_word == cmd for cmd in ["kick", "unkick", "pending rooms", "accept pending"]):
                commands = user_commands
            else:
                commands = base_commands

        options = [i for i in commands if i.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    return completer

def admin_cmd(server:'Server'):
    """
    Admin commands to manage the server.

    :param Server server: The server.
    """
    readline.parse_and_bind("tab: complete")
    readline.set_completer(create_completer(server))

    while not server.stop_server:
        command = input("> ")
        readline.add_history(command)
        if command == "help":
            print("""Available commands:
help - display this help message

messages <time> - display a list of all messages since a time
users - display a list of all users

rooms - display a list of all rooms
add room <room1,room2,...> - add a room
pending rooms <username> - display a list of pending rooms for a user
accept pending <username> <room1,room2,...> - accept pending rooms for a user

kick <username> <timeout> <reason> - kick a user
unkick <username> - unkick a user

ban <username> <reason> - ban a user
ban ip <ip> <reason> - ban an IP address
unban <username> - unban a user
unban ip <ip> - unban an IP address")

shutdown - shutdown the server""")

        ########################################################################################################

        elif command.startswith("messages"):
            try:
                date = convert_to_date_minus(command.split(" ")[1])
                print(f"Messages since {date}:")
                ## Get messages in the database since the date
                for message in server.database.fetch_messages_since(date):
                    ## Convert the date to a string
                    date_str = message[2].strftime("%Y-%m-%d %H:%M:%S")
                    print(message[0] + " in " + message[1] + " at " + date_str + " : " + message[3])
            except IndexError:
                print("Please specify a date")
        
        elif command == "users":
            print("Users:")
            for user in server.clients:
                print(user.name + " " + user.ip[0])
        
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
                                # Check if the user is already in the room
                                if room not in client.rooms:
                                    client.addroom(server, room) 
                            break
                else:
                    for room in rooms.split(","):
                        for client in server.clients:
                            if client.name == username:
                                # Check if the user is already in the room
                                if room not in client.rooms:
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
                    print("Please specify a username and a duration")
        
        elif command.startswith("unkick"):
            if command.split(" ")[1] == "ip":
                try:
                    ip = command.split(" ")[2]
                    server.unkick_ip(ip)
                except IndexError:
                    print("Please specify an IP address and a duration")
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
