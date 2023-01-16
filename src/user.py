import uuid


class User:

    def __init__(self, host, port, client_name, nick, connection):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.connection = connection
        self.nick = nick
        self.current_channel = None
        self.id = uuid.uuid4()

    def set_nick(self, nick: str, nicks: list[str]):
        if nick in nicks:
            return False

        self.nick = nick
        return True

    def set_current_channel(self, channel_name: str):
        self.current_channel = channel_name

    def quit_current_channel(self):
        self.current_channel = None

    def get_user(self):
        return f"{self.nick} {self.host} {self.client_name}"
