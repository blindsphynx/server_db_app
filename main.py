from src.http_server import Server

if __name__ == '__main__':
    server = Server()
    server.run()
    # server.connect_to_postgesql()
    # my_query = "SELECT * FROM students"
    # server.readFromDatabase(my_query)
    # server.shutdown_DB_connection()
    # sys.exit(server.close())
