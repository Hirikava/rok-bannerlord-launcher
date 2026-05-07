import typing
from socket import socket


@typing.final
class SystemUtils:

    @staticmethod
    def get_free_port():
        sock = socket()
        sock.bind(("127.0.0.1", 0))
        (host, port) = sock.getsockname()
        sock.close()
        return port
