# Cliente TCP
import socket


class Client:
    """Handles connection with the server."""

    def __init__(self, host, port, client_name) -> None:
        self.host = host
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        self.client_name = client_name

    def connect(self):
        """Connects with the server on the host and ports initialized and send the client name"""
        self.tcp_socket.connect((self.host, self.port))
        client.send_message(self.client_name.encode())

    def send_message(self, msg):
        """
        Sends message to the server
        Obs: msg must be a byte
        """
        self.tcp_socket.send(msg)

    def close_connection(self):
        """Closes connection with the server"""
        self.tcp_socket.close()


client = Client("127.0.0.1", 5002, "Desktop top")
client.connect()

while True:
    msg = input()
    if msg == "End":
        client.close_connection()
        break
    client.send_message(msg.encode())
