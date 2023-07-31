from Server import server, connect_to_postgresql, DBconnection, DBcursor

if __name__ == '__main__':
    connect_to_postgresql(DBconnection, DBcursor)
    server.run(debug=True, port=8000)
