import psycopg2


class Server:
    def __init__(self):
        self.connection = psycopg2.connect(dbname='postgres1', user='user', password='pyro127',
                                           host='localhost', port='5432')
        self.connection.autocommit = True

    def connectToDatabase(self):
        pass

    def shutdown(self):
        self.connection.close()

    def writeToDatabase(self, query):
        pass

    def readFromDatabase(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        print("id\tname\tpoints")
        for line in records:
            print(*line, sep="\t")
        cursor.close()
