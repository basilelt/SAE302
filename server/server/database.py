from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

class DatabaseConnection:
    """
    A class used to represent a Database Connection.

    ...

    Attributes
    ----------
    engine : Engine
        a SQLAlchemy Engine that represents the core interface to the database

    Methods
    -------
    connect():
        Connects to the MySQL database.
    execute_sql_query(query, params=None):
        Executes a SQL query with optional parameters.
    fetch_one(query, params=None):
        Executes a SQL query and fetches one record.
    fetch_all(query, params=None):
        Executes a SQL query and fetches all records.
    fetch_user_state(user):
        Fetches the state of a user from the database.
    user_exists(user):
        Checks if a user exists in the database.
    fetch_user_password(user):
        Fetches the password of a user from the database.
    room_exists(room):
        Checks if a room exists in the database.
    insert_message(user, room, date_message, ip, body):
        Inserts a message into the database.
    """

    def __init__(self):
        """Initializes the DatabaseConnection object with a None engine."""
        self.engine = None

    def connect(self):
        """Connects to the MySQL database."""
        try:
            self.engine = create_engine("mysql+pymysql://chat:chat@localhost/chat", poolclass=QueuePool)
        except SQLAlchemyError as e:
            print(f"Error connecting to database: {e}")

    def execute_sql_query(self, query, params=None):
        """Executes a SQL query with optional parameters."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params)
                connection.commit()
                return result
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")

    def fetch_one(self, query, params=None):
        """Executes a SQL query and fetches one record."""
        result = self.execute_sql_query(query, params)
        if result:
            return result.fetchone()

    def fetch_all(self, query, params=None):
        """Executes a SQL query and fetches all records."""
        result = self.execute_sql_query(query, params)
        if result:
            return result.fetchall()

    def fetch_user_state(self, user):
        """Fetches the state of a user from the database."""
        result = self.fetch_one("SELECT state FROM users WHERE name = :user",
                                {'user': user})
        return result[0] if result else None

    def user_exists(self, user):
        """Checks if a user exists in the database."""
        result = self.fetch_one("SELECT name FROM users WHERE name = :user",
                                {'user': user})
        return len(result) > 0 if result else False

    def fetch_user_password(self, user):
        """Fetches the password of a user from the database."""
        result = self.fetch_one("SELECT password FROM users WHERE name = :user",
                                {'user': user})
        return result[0].encode('utf-8') if result else None
    
    def get_rooms(self):
        """Fetches all rooms from the database."""
        result = self.fetch_all("SELECT name FROM rooms")
        return [room[0] for room in result] if result else None

    def room_exists(self, room):
        """Checks if a room exists in the database."""
        result = self.fetch_one("SELECT name FROM rooms WHERE name = :room",
                                {'room': room})
        return len(result) > 0 if result else False

    def insert_message(self, user, room, date_message, ip, body):
        """Inserts a message into the database."""
        self.execute_sql_query("INSERT INTO messages (user, room, date_message, ip, body) VALUES (:user, :room, :date_message, :ip, :body)",
                               {'user': user,
                                'room': room,
                                'date_message': date_message,
                                'ip': ip,
                                'body': body})
        
    def close(self):
        """Closes the database connection."""
        self.engine.dispose()
