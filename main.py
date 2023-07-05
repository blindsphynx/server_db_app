# from src.flask_server import server, connect_to_postgesql, DBcursor, DBconnection
from src.Server import server, connect_to_postgesql, DBconnection

if __name__ == '__main__':
    connect_to_postgesql(DBconnection)
    server.run(debug=True, port=8000)

# if __name__ == '__main__':
#     connect_to_postgesql(DBconnection, DBcursor)
#     server.run(debug=True, port=8000)
    # server.shutdown_DB_connection()
    # sys.exit(server.close())
