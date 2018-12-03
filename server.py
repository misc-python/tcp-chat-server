from client import Client
import threading
import socket

PORT = 4547


class ChatServer(threading.Thread):
    def __init__(self, port, host='localhost'):
        super().__init__(daemon=True)
        self.port = PORT
        self.host = host
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            )
        self.client_pool = []

        try:
            self.server.bind((self.host, self.port))
        except socket.error:
            print(f'bind failed { socket.error }')

        self.server.listen(10)

    def parser(self, id, nick, conn, message):
        """Parse the message out to look for keywords."""
        if message.decode().startswith('/'):
            data = message.decode().split(maxsplit=1)

            if data[0] == '/quit':
                conn.sendall(b'You have left the chat.')
                reply = nick.encode() + b'has left the channel.\n'
                [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.id != id]
                conn.close()

            if data[0] == '/list':
                reply = ''
                for c in self.client_pool:
                    reply += c.nick + ' \n'
                [c.conn.sendall(reply.encode()) for c in self.client_pool if len(self.client_pool)]
                return('')

        else:
            reply = nick.encode() + b': ' + message
            [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
            return('')

    def run_thread(self, id, nick, conn, addr):
        """ changes the nickname and establishes connection"""
        print('{} connected with {}:{}'.format(nick, addr[0], str(addr[1])))
        try:
            while True:
                data = conn.recv(4096)
                parsed_nickname = self.parser(id, nick, conn, data)
                if len(parsed_nickname):
                    nick = parsed_nickname
        except (ConnectionResetError, BrokenPipeError, OSError):
            conn.close()

    def run(self):
        """ Runs the server."""
        print('Server running on {}'.format(PORT))
        while True:
            conn, addr = self.server.accept()
            client = Client(conn, addr)
            self.client_pool.append(client)
            threading.Thread(
                target=self.run_thread,
                args=(client.id, client.nick, client.conn, client.addr),
                daemon=True
                ).start()

    def exit(self):
        """Close the connection."""
        self.server.close()


if __name__ == '__main__':
    server = ChatServer(PORT)
    try:
        server.run()
    except KeyboardInterrupt:
        [c.conn.close() for c in server.client_pool if len(server.client_pool)]
        server.exit()
