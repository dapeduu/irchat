# Servidor TCP
import socket
from threading import Thread
from user import User
from channel import Channel


class Server:
    """Handles server creation and handling"""

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.channels = {
            "Canal 1": Channel("Canal 1"),
            "Canal 2": Channel("Cannal 2")
        }
        self.users = {}

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((host, port))

    def listen(self):
        """Listen to connections and send them to a thread"""
        failed_connections_allowed_before_refusing = 1
        self.tcp_socket.listen(failed_connections_allowed_before_refusing)

    def accept_connection(self):
        """Accepts client connection and set a thread to handle it"""
        connection, client_address = self.tcp_socket.accept()

        client_name = connection.recv(1024)
        user = User(connection=connection,
                    host=client_address[0],
                    port=client_address[1],
                    client_name=client_name)

        self.users[user.nick] = user

        print('Conected with ', client_address)

        t = Thread(target=self.__connection, args=(
            connection, client_address, user.nick))
        t.start()

    def __connection(self, connection: socket.socket, client_address, nick):
        """Hanndles the received messages"""
        while True:
            msg = connection.recv(1024)
            if not msg:
                break
            print(msg.decode())

            # Aqui recebemos as mensagens e vamos chamar nossos handlers
            if msg.decode() == "users":
                print(self.users.keys())

        self.users.pop(nick)
        connection.close()
        print('Finished client connection', client_address)


server = Server("127.0.0.1", 5002)
server.listen()
server.accept_connection()
server.accept_connection()
