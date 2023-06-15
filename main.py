from http_server import Server

server = Server()
query = 'SELECT * FROM students'
server.readFromDatabase(query)

server.shutdown()
