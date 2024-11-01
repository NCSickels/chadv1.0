from .ifuzzer import IFuzzer
from fuzzowski import Session
from fuzzowski.mutants.spike import *


class FTP(IFuzzer):
    """FTP Fuzzer"""

    name = 'ftp'

    @staticmethod
    def get_requests() -> List[callable]:
        """Get possible requests"""
        return [FTP.put, FTP.get]

    @staticmethod
    def define_nodes(*args, **kwargs) -> None:
        # Put
        s_initialize('put')
        s_static(b'\x00\x01', name="command")
        s_string("username", name="username")
        s_delim()
        s_string("password", name="password")
        s_delim()
        s_string("remote_path", name="remote_path")
        s_delim()
        s_string("local_path", name="local_path")

        # Get
        s_initialize('get')
        s_static(b'\x00\x02', name="command")
        s_string("username", name="username")
        s_delim()
        s_string("password", name="password")
        s_delim()
        s_string("remote_path", name="remote_path")

    @staticmethod
    def put(session: Session) -> None:
        session.connect(s_get('put'))

    @staticmethod
    def get(session: Session) -> None:
        session.connect(s_get('get'))
