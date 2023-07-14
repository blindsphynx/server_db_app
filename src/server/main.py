from Server import server, connect_to_postgesql, DBconnection, DBcursor

if __name__ == '__main__':
    connect_to_postgesql(DBconnection, DBcursor)
    server.run(debug=True, port=8000)
