from src.flask_server import server, connect_to_postgesql, DBcursor, DBconnection

if __name__ == '__main__':
    connect_to_postgesql(DBconnection, DBcursor)
    server.run(debug=True, port=8000)
    # my_query = "SELECT * FROM students"
    # server.readFromDatabase(my_query)
    # server.shutdown_DB_connection()
    # sys.exit(server.close())
