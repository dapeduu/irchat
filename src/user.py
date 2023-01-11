class User:
    count = 0

    def __init__(self, host, port, client_name, connection) -> None:
        User.count += 1
        self.host = host
        self.port = port
        self.client_name = client_name
        self.connection = connection
        self.nick = f"Usuário {User.count}"

    def setNick(self, nick):
        self.nick = nick
        # Adicionar verificação se o nick é único

    def set_current_channel(self, channel_name):
        self.current_channel = channel_name

    def getSelf(self):
        return {
            "host": self.host,
            "port": self.port,
            "client_name": self.client_name,
            "nick": self.nick
        }
