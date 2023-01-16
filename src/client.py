# Cliente TCP
import socket
from threading import Thread


class Client:
    """Handles connection with the server."""

    def __init__(self, host=None, port=None, client_name=None, initial_nick=None) -> None:
        self.host = host if host else input("Endereço de ip do servidor:\n")
        self.port = port if port else int(
            input("Número da porta do servidor:\n"))
        self.tcp_socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        self.client_name = client_name if client_name else input("Seu nome:\n")
        self.initial_nick = initial_nick if initial_nick else input(
            "Seu apelido:\n")
        self.running = False

        self.connect()

    def connect(self):
        """Connects with the server on the host and ports initialized and send the client name"""
        self.tcp_socket.connect((self.host, self.port))

        client_nick_and_name = f"{self.client_name} {self.initial_nick}"
        self.send_message(client_nick_and_name.encode())

        self.running = True

        t_receive_messages = Thread(target=self.receive_messages_loop)
        t_send_messages = Thread(target=self.send_messages_loop)
        t_receive_messages.start()
        t_send_messages.start()

    def send_message(self, msg):
        """
        Sends message to the server
        Obs: msg must be a byte
        """
        self.tcp_socket.send(msg)

    def receive_message(self):
        return self.tcp_socket.recv(1024).decode() + "\n"

    def close_connection(self):
        """Closes connection with the server"""
        self.running = False
        self.tcp_socket.close()

    def receive_messages_loop(self):
        while self.running:
            msg = self.receive_message()
            print(msg)

    def send_messages_loop(self):

        while self.running:
            msg = input()
            self.send_message(msg.encode())

            if msg == "\x18" or msg == "QUIT":
                self.running = False


Client("192.168.3.4", 5002, "Pedro")
