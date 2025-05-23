"""Interface for connections to attack target."""

import abc


class ITargetConnection(object):
    """
    Interface for connections to attack target.
    Target connections may be opened and closed multiple times. You must open before using send/recv and close
    afterwards.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def close(self) -> None:
        """
        Close connection.

        :return: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def open(self) -> None:
        """
        Opens connection to the target. Make sure to call close!

        :return: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def recv(self, max_bytes: int) -> bytes:
        """
        Receive up to max_bytes data.

        :param max_bytes: Maximum number of bytes to receive.
        :type max_bytes: int

        :return: Received data. bytes('') if no data is received.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def recv_all(self, max_bytes: int) -> bytes:
        """
        Receive up to max_bytes data, trying to receive everything coming.

        :param max_bytes: Maximum number of bytes to receive.
        :type max_bytes: int

        :return: Received data. bytes('') if no data is received.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def send(self, data: bytes) -> int:
        """
        Send data to the target.

        :param data: Data to send.

        :rtype int
        :return: Number of bytes actually sent.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def info(self) -> str:
        """Return description of connection info.

        E.g., "127.0.0.1:2121"

        Returns:
            str: Connection info descrption
        """
        raise NotImplementedError
