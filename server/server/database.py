from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class DatabaseConnection:
    def __init__(self):
        self.engine = None

    def connect(self):
        self.engine = create_engine("mysql+pymysql://root:@localhost/chat", poolclass=QueuePool)

    def execute_sql_query(self, query, params=None):
        with self.engine.connect() as connection:
            result = connection.execute(query, params)
            return result

    def fetch_one(self, query, params=None):
        result = self.execute_sql_query(query, params)
        return result.fetchone()

    def fetch_all(self, query, params=None):
        result = self.execute_sql_query(query, params)
        return result.fetchall()

    def fetch_user_state(self, user):
        result = self.fetch_one("SELECT etat FROM utilisateurs WHERE nom = %s", (user,))
        return result[0] if result else None