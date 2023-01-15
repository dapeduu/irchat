# Cliente TCP
import socket
from threading import Thread


class Client:
    """Handles connection with the server."""

    def __init__(self, host, port, client_name) -> None:
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        self.client_name = client_name
        self.running = False

    def connect(self):
        """Connects with the server on the host and ports initialized and send the client name"""
        self.tcp_socket.connect((self.host, self.port))
        client.send_message(self.client_name.encode())
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
        return self.tcp_socket.recv(1024).decode()

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


client = Client("127.0.0.1", 5002, "Desktop top")
client.connect()
