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
            "Canal1": Channel("Canal1"),
            "Canal2": Channel("Cannal2")
        }
        self.users: dict[str, User] = {}

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((host, port))

    def listen(self):
        """Listen to connections and send them to a thread"""
        failed_connections_allowed_before_refusing = 1
        self.tcp_socket.listen(failed_connections_allowed_before_refusing)

    def accept_connection(self):
        """Accepts client connection and set a thread to handle it"""
        connection, client_address = self.tcp_socket.accept()

        client_name = connection.recv(1024).decode()
        user = User(connection=connection,
                    host=client_address[0],
                    port=client_address[1],
                    client_name=client_name)

        self.users[user.nick] = user

        print('Conected with ', client_address)
        connection.send(b"Connected")

        t = Thread(target=self.__connection, args=(
            connection, client_address, user.nick))
        t.start()

    def __connection(self, connection: socket.socket, client_address, current_user_nickname: str):
        """Hanndles the received messages"""
        while True:
            msg = connection.recv(1024)
            if not msg:
                break

            msg_tokens = msg.decode().split()
            command = msg_tokens[0]

            response = None

            if command == "LIST":
                response = self.list_channels()

            elif command == "JOIN":
                channel = msg_tokens[1]
                response = self.join_channel(
                    channel, self.users[current_user_nickname])

            elif command == "PART":
                channel = msg_tokens[1]
                response = self.part_channel(
                    channel, self.users[current_user_nickname])

            elif command == "NICK":
                new_nickname = msg_tokens[1]
                current_users = list(self.users.keys())
                success = self.users[current_user_nickname].set_nick(
                    new_nickname, current_users)

                if success:
                    self.users[new_nickname] = self.users.pop(
                        current_user_nickname)
                else:
                    response = "Username already picked"

            elif command == "USER":
                user_nickname = msg_tokens[1]
                response = self.user(user_nickname)

            elif command == "WHO":
                channel_name = msg_tokens[1]
                response = self.who(channel_name)

            elif command == "PRIVMSG":
                destination = msg_tokens[1]  # Channel or User
                response = self.priv_message(
                    current_user_nickname, destination, msg_tokens)

            elif command == "QUIT":
                connection.close()
                print('Manually finished client connection', client_address)
                break
            else:
                print("ERR UNKNOWNCOMMAND")

            if response != None:
                connection.send(response.encode())

        self.users.pop(current_user_nickname)
        connection.close()
        print('Finished client connection', client_address)

    def user(self, nickname: str):
        if nickname not in list(self.users.keys()):
            return "User not found"

        user = self.users[nickname]

        return user.get_user()

    def who(self, channel_name: str):
        if channel_name not in list(self.channels.keys()):
            return "Channel not found"

        channel = self.channels[channel_name]
        channel_users_list = list(channel.users.keys())
        channel_users = " ".join(
            channel_users_list) if len(channel_users_list) > 0 else "No users"

        return f"{channel_name} - {channel_users}"

    def priv_message(self, sender: str, destination: str, msg_tokens: list[str]):
        is_for_user = False
        is_for_channel = False

        for user in list(self.users.keys()):
            if user != destination:
                continue
            is_for_user = True
        for channel in list(self.channels.keys()):
            if channel != destination:
                continue
            is_for_channel = True

        msg = f"{sender} - " + " ".join(msg_tokens).split(" ", 2)[-1]

        if is_for_user:
            self.users[destination].connection.send(
                msg.encode())
        if is_for_channel:
            for user in self.channels[destination].users.values():
                user.connection.send(msg.encode())

        if not (is_for_channel or is_for_user):
            return "User or Channel not found"

        return None

    def list_channels(self):
        channels_list = []
        for channel_name, channel in self.channels.items():
            channels_list.append(
                f"{channel_name} - {len(list(channel.users.keys()))}")

        return "Lista de Canais: \n" + "\n".join(channels_list)

    def join_channel(self, channel_name: str, user: User):
        if channel_name not in self.channels.keys():
            return "Invalid channel name"

        user_current_channel = self.users[user.nick].current_channel
        if user_current_channel != None:
            self.part_channel(user=user, channel_name=user_current_channel)

        self.channels[channel_name].add_user(user)
        self.users[user.nick].set_current_channel(channel_name)

        return f"Joined {channel_name} successfully"

    def part_channel(self, channel_name: str, user: User):
        if channel_name not in self.channels.keys():
            return "Invalid channel name"
        if user.nick not in list(self.channels[channel_name].users.keys()):
            return "User is not part of this channel"

        self.channels[channel_name].remove_user(user.nick)
        self.users[user.nick].quit_current_channel()

        return f"Parted from {channel_name} successfully"


server = Server("127.0.0.1", 5002)
server.listen()
server.accept_connection()
server.accept_connection()
