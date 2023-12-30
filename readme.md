# SAE302 - Chat Server

**A chat server written in Python.**

*Tested on Python 3.11 and 3.12 on a Unix system only.*

This project consist of a server (command line) and a client (graphic).

You can:
* Create users
* Join rooms
* Send private messages
* Ban/kick/kill a user
* See the history of messages
* See users connected
* Add new rooms

The default rooms are:
* Blabla (can be joined without approval)
* Comptabilité
* Général (automatically joined on user creation)
* Informatique
* Marketing

## Client installation

After installing Python and cloning the git:

```bash
python -m venv "path_to_your_venv"
source "path_to_your_venv"/bin/activate

pip install -r client/requirements.txt
```

## Usage Client
```bash
source "path_to_your_venv"/bin/activate

python client/main.py
```

## Server installation

After installing Python and cloning the git:

```bash
python -m venv "path_to_your_venv"
source "path_to_your_venv"/bin/activate

pip install -r server/requirements.txt
```
The database is using MySQL and should be imported:
```bash
└── server
    └── db
        └── chat.sql -> database to import
```
```bash
mysql -u root -p chat < server/db/chat.sql
```


## Usage Server
```bash
source "path_to_your_venv"/bin/activate

python server/main.py -a <ip_to_use> -p <port_to_use>
```
**Commands of the server:**
```
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
unban ip <ip> - unban an IP address
kill <username> <reason> - kill a user

shutdown - shutdown the server
```

## Contributing

Here is the structure of the project:
```bash

client
├── backend
│   ├── client.py -> client class
│   ├── handler.py -> redirects messages
│   └── types.py -> handles messages content
├── interface
│   ├── chat.py -> chat window class
│   ├── error.gif
│   ├── login.css
|   └── login.py -> login window class
├── main.py -> starts the programm
└── requirements.txt
server
├── db
|   └── chat.sql -> database to import
├── server
│   ├── admin.py -> handles commands in the terminal
│   ├── client.py -> client class
│   ├── database.py -> database class (database logic)
│   ├── message_handler.py -> redirects messages
│   ├── server.py -> server class
|   └── types.py -> handles messages content
├── main.py -> start the programm
└── requirements.txt   
```

Here is the structure of the database:
![dbdiagram](https://github.com/basilelt/SAE302/blob/main/docs/sql/dbdiagram.png?raw=true)

You can also find a docstring sphinx for the [client](https://yourusername.github.io/yourrepository/client.html) and the [server](https://yourusername.github.io/yourrepository/server.html).

## Notes
This chat server shouldn't be used outside of a local trusted network as the data traffic isn't encrypted:
* messages are sent in clear
* passwords are sent in clear
* messages could be forged


Messages can't be sent to users not connected to the server.

Even if all messages are stored on the server those aren't served when a client connect, meaning the history of a room isn't readable by clients.
