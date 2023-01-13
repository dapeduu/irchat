from user import User


class Channel:
    def __init__(self, name) -> None:
        self.users: dict[str, User] = {}
        self.name = name

    def add_user(self, user: User):
        self.users[user.nick] = user

    def remove_user(self, nick):
        self.users.pop(nick)
