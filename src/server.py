# Servidor TCP
import socket
from threading import Thread


class Server:
    """Handles server creation and handling"""

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((host, port))

    def run(self):
        """Listen to connections and send them to a thread"""
        failed_connections_allowed_before_refusing = 1
        self.tcp_socket.listen(failed_connections_allowed_before_refusing)

        print(
            f'Server is listening to connections on {(self.host, self.port)}')

        while True:
            connection, client = self.tcp_socket.accept()
            print('Conected with ', client)
            t = Thread(target=self.__connection, args=(connection, client))
            t.start()

    def __connection(self, connection: socket.socket, client):
        """Hanndles the received messages"""
        while True:
            msg = connection.recv(1024)
            if not msg:
                break
            # Aqui recebemos as mensagens e vamos chamar nossos handlers
            print(str(msg, encoding='utf-8'))
        connection.close()
        print('Finished client connection', client)
