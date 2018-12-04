import random
import uuid


class Client:
    """Create and instantiate a Client class."""

    def __init__(self, conn=None, addr=None):
        self.id = str(uuid.uuid4())
        self.nick = f'user_{random.random()}'
        self.conn = conn
        self.addr = addr

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def change_nickname(self, nick):
        """Create the change nickname method."""
        self.nick = nick
        return(self)
