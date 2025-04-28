import mysql.connector

class DBManager:
    def __init__(self, host='localhost', user='root', password='Blackjack', database='blackjack'):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE,
                balance INT DEFAULT 1000,
                highscore INT DEFAULT 0
            )
        """)
        self.connection.commit()

    def get_player(self, name):
        self.cursor.execute("SELECT balance, highscore FROM players WHERE name = %s", (name,))
        return self.cursor.fetchone()

    def create_player(self, name):
        self.cursor.execute("INSERT INTO players (name) VALUES (%s)", (name,))
        self.connection.commit()

    def update_player(self, name, balance, highscore):
        self.cursor.execute("""
            UPDATE players 
            SET balance = %s, highscore = GREATEST(highscore, %s) 
            WHERE name = %s
        """, (balance, highscore, name))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
