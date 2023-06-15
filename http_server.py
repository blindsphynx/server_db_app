from tabulate import tabulate
import psycopg2


class Server:
    def __init__(self):
        self.connection = psycopg2.connect(dbname='postgres1', user='user', password='pyro127',
                                           host='localhost', port='5432')
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        print("[INFO] PostgreSQL connection established")

    def shutdown(self):
        self.connection.close()
        print("[INFO] PostgreSQL connection closed")

    def writeToDatabase(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()

    def readFromDatabase(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        table = []
        for line in records:
            table.append([*line])

        print(tabulate(table, headers=["id", "name", "year", "photo", "course", "class"], tablefmt='orgtbl'))
        self.cursor.close()
