"""Custom exceptions for every module of the Chad application."""

import attrs


class ChadError(Exception):
    """Base exception for all Chad errors."""

    pass


class ChadRestartFailedError(ChadError):
    pass


class ChadTargetConnectionFailedError(ChadError):
    pass


class ChadPausedError(ChadError):
    pass


class ChadTargetConnectionReset(ChadError):
    pass


class ChadTargetRecvTimeout(ChadError):
    pass


@attrs.define
class ChadTargetConnectionAborted(ChadError):
    """
    Raised on `errno.ECONNABORTED`.
    """

    socket_errno: int = attrs.field()
    socket_errmsg: str = attrs.field()


class ChadRuntimeError(ChadError):
    pass


class ChadPacketCaptureInterrupted(ChadError):
    """
    Raised when packet capture is interrupted by user.
    """

    pass


class ChadProgramExit(ChadError):
    pass


class ModuleException(Exception):
    pass
