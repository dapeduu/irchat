# Servidor TCP
import socket
from threading import Thread
from user import User
from channel import Channel
import uuid


class Server:
    """Handles server creation and handling"""

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.channels = {
            "Canal1": Channel("Canal1"),
            "Canal2": Channel("Cannal2")
        }
        self.users: dict[uuid.UUID, User] = {}

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((host, port))

    def listen(self):
        """Listen to connections and send them to a thread"""
        failed_connections_allowed_before_refusing = 1
        self.tcp_socket.listen(failed_connections_allowed_before_refusing)

    def accept_connection(self):
        """Accepts client connection and set a thread to handle it"""

        connection, client_address = self.tcp_socket.accept()
        connection.send(b"Conectado ao servidor!")
        print('Conected with ', client_address)

        client_name_and_nick = connection.recv(1024).decode().split()
        client_name = client_name_and_nick[0]
        client_nick = client_name_and_nick[1]

        user = User(connection=connection,
                    host=client_address[0],
                    port=client_address[1],
                    nick=client_nick,
                    client_name=client_name)

        self.users[user.id] = user

        t = Thread(target=self.__connection, args=(
            connection, client_address, user.id))
        t.start()

    def __connection(self, connection: socket.socket, client_address, current_user_id: uuid.UUID):
        """Hanndles the received messages"""
        while True:
            msg = connection.recv(1024)
            if not msg:
                break

            msg_tokens = msg.decode().split()
            command = msg_tokens[0]

            response = None

            commands_with_two_or_more_arguments = [
                "JOIN", "PART", "NICK", "USER", "WHO", "PRIVMSG"]

            if command in commands_with_two_or_more_arguments and len(msg_tokens) <= 1:
                response = "Número inválido de argumentos"
            else:
                if command == "LIST":
                    response = self.list_channels()

                elif command == "JOIN":
                    channel = msg_tokens[1]
                    response = self.join_channel(
                        channel, self.users[current_user_id])

                elif command == "PART":
                    channel = msg_tokens[1]
                    response = self.part_channel(
                        channel, self.users[current_user_id])

                elif command == "NICK":
                    new_nickname = msg_tokens[1]
                    current_users = [user.nick for user in list(
                        self.users.values())]  # list(self.users.values())
                    success = self.users[current_user_id].set_nick(
                        new_nickname, current_users)

                    if success:
                        response = "Nick alterado"
                    else:
                        response = "Esse nick já está em uso"

                elif command == "USER":
                    user_nickname = msg_tokens[1]
                    response = self.user(user_nickname)

                elif command == "WHO":
                    channel_name = msg_tokens[1]
                    response = self.who(channel_name)

                elif command == "PRIVMSG":
                    destination = msg_tokens[1]  # Channel or User
                    response = self.priv_message(
                        self.users[current_user_id].nick, destination, msg_tokens)

                elif command == "QUIT":
                    connection.close()
                    print('Manually finished client connection', client_address)
                    break
                else:
                    response = "[ERRO] Comando desconhecido"
                    print("ERR UNKNOWNCOMMAND")

            if response != None:
                connection.send(response.encode())

        self.users.pop(current_user_id)
        connection.close()
        print('Finished client connection', client_address)

    def user(self, nickname: str):
        user_id = self.get_user_id_from_nick(nick=nickname)

        if not user_id:
            return "Usuário não encontrado"

        user = self.users[user_id]

        return user.get_user()

    def who(self, channel_name: str):
        if channel_name not in list(self.channels.keys()):
            return "Canal não encontrado"

        channel = self.channels[channel_name]
        channel_users_list = list(channel.users.keys())
        channel_users = " ".join(
            channel_users_list) if len(channel_users_list) > 0 else "Sem usuários no momento"

        return f"{channel_name} - {channel_users}"

    def priv_message(self, sender: str, destination: str, msg_tokens: list[str]):
        is_for_user = False
        is_for_channel = False

        for user in self.users.values():
            if user.nick != destination:
                continue
            is_for_user = True
        for channel in self.channels.keys():
            if channel != destination:
                continue
            is_for_channel = True

        full_msg = " ".join(msg_tokens).split(" ", 2)[-1]

        if is_for_user:
            receiver_id = self.get_user_id_from_nick(destination)

            if not receiver_id:
                return "Usuário ou Canal não encontrado"

            self.send_msg_for_user(
                sender=sender, receiver_id=receiver_id, msg=full_msg)

        if is_for_channel:
            self.send_msg_for_channel(
                channel_name=destination, sender=sender, msg=full_msg)

        if not (is_for_channel or is_for_user):
            return "Usuário ou Canal não encontrado"

        return None

    def get_user_id_from_nick(self, nick: str):
        id = None

        for user in self.users.values():

            if user.nick == nick:
                id = user.id

        return id

    def list_channels(self):
        channels_list = []
        for channel_name, channel in self.channels.items():
            channels_list.append(
                f"{channel_name} - {len(list(channel.users.keys()))}")

        return "Lista de Canais: \n" + "\n".join(channels_list)

    def join_channel(self, channel_name: str, user: User):
        if channel_name not in self.channels.keys():
            return "[ERRO] Nome de canal inválido"

        user_current_channel = self.users[user.id].current_channel
        if user_current_channel != None:
            self.part_channel(user=user, channel_name=user_current_channel)

        self.channels[channel_name].add_user(user)
        self.users[user.id].set_current_channel(channel_name)

        return f"Entrou no canal {channel_name}"

    def part_channel(self, channel_name: str, user: User):
        if channel_name not in self.channels.keys():
            return "[ERRO] Nome de canal inválido"
        if user.nick not in list(self.channels[channel_name].users.keys()):
            return "[ERRO] O usuário não é parte desse canal"

        self.channels[channel_name].remove_user(user.nick)
        self.users[user.id].quit_current_channel()

        return f"Saiu do canal {channel_name}"

    def send_msg_for_channel(self, channel_name: str, sender: str, msg: str):
        msg_for_channel = f"[{channel_name} - {sender}] {msg}"
        for user in self.channels[channel_name].users.values():
            if user.nick == sender:  # Dont send message for the sender
                continue
            user.connection.send(msg_for_channel.encode())

    def send_msg_for_user(self, sender: str, receiver_id: uuid.UUID, msg):
        msg_for_user = f"[{sender}] {msg}"
        self.users[receiver_id].connection.send(
            msg_for_user.encode())


server = Server("192.168.3.4", 5002)
server.listen()
server.accept_connection()
server.accept_connection()
server.accept_connection()
