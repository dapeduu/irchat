# Cliente TCP
import socket


class Client:
    """Handles connection with the server."""

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)

    def connect(self):
        """Connects with the server on the host and ports initialized"""
        self.tcp_socket.connect((self.host, self.port))

    def send_message(self, msg):
        """
        Sends message to the server
        Obs: msg must be a byte
        """
        self.tcp_socket.send(msg)

    def close_connection(self):
        """Closes connection with the server"""
        self.tcp_socket.close()


client = Client("127.0.0.1", 5002)
client.connect()
client.send_message(b"PRIVMSG Lemos asdjasdkjandkhakd")
