import mysql.connector

class DatabaseConnector:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(255) PRIMARY KEY,
                    name TEXT
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255),
                    date_time DATETIME,
                    action TEXT,
                    elapsed_time TIME,
                    late BOOLEAN,
                    absent BOOLEAN,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255)
                )
            ''')

            self.conn.commit()

        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")

    def create_user(self, user_id, name):
        try:
            self.cursor.execute("INSERT INTO users (id, name) VALUES (%s, %s)", (user_id, name))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error creating user: {err}")

    def execute_query(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def fetch_one(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchone()

    def fetch_all(self, query, values=None):
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
            return None

    def close_connection(self):
        self.conn.close()
