"""Helpers for the network connection modules."""

import ctypes
import errno
import json
import os
import platform
import re
import signal
import socket
import struct
import time
import zlib
from datetime import datetime, timezone
from functools import reduce
from itertools import groupby

from prompt_toolkit import HTML
from prompt_toolkit.formatted_text import FormattedText

from modules.utils import constants, ip_constants

test_step_info = {
    "test_case": {
        "indent": 0,
        "title": "Test Case",
        "html": "Test Case: {msg}",
        "terminal": "Test Case: {msg}",
        "css_class": "log-case",
    },
    "step": {
        "indent": 1,
        "title": "Test Step",
        "html": " Test Step: {msg}",
        "terminal": "Test Step: {msg}",
        "css_class": "log-step",
    },
    "info": {
        "indent": 2,
        "title": "Info",
        "html": "Info: {msg}",
        "terminal": "Info: {msg}",
        "css_class": "log-info",
    },
    "error": {
        "indent": 2,
        "title": "Error",
        "html": "Error!!!! {msg}",
        "terminal": "Error!!!! {msg}",
        "css_class": "log-error",
    },
    "send": {
        "indent": 2,
        "title": "Transmitting",
        "html": "Transmitting {n} bytes: {msg}",
        "terminal": "Transmitting {n} bytes: {msg}",
        "css_class": "log-send",
    },
    "receive": {
        "indent": 2,
        "title": "Received",
        "html": "Received: {msg}",
        "terminal": "Received: {msg}",
        "css_class": "log-receive",
    },
    "check": {
        "indent": 2,
        "title": "Check",
        "html": "Check: {msg}",
        "terminal": "Check: {msg}",
        "css_class": "log-check",
    },
    "fail": {
        "indent": 2,
        "title": "Check Failed",
        "html": "Check Failed: {msg}",
        "terminal": "Check Failed: {msg}",
        "css_class": "log-fail",
    },
    "pass": {
        "indent": 2,
        "title": "Check OK",
        "html": "Check OK: {msg}",
        "terminal": "Check OK: {msg}",
        "css_class": "log-pass",
    },
    "warning": {
        "indent": 2,
        "title": "Warn",
        "html": "Warn: {msg}",
        "terminal": "Warn: {msg}",
        "css_class": "log-fail",
    },
}


def color_html(data: str, msg_type: str) -> HTML:
    if msg_type in constants.STYLE:
        return HTML("<{}>{}</{}>".format(msg_type, data, msg_type))
    else:
        return HTML(data)


def color_formatted_text(data: str, msg_type: str) -> FormattedText:
    if msg_type in constants.STYLE:
        return FormattedText([("class:{}".format(msg_type), data)])
    else:
        return FormattedText([("", data)])


def ip_str_to_bytes(ip: str) -> bytes:
    """
    Convert an IP string to a four-byte bytes.

    Args:
        ip (str): IP address string, e.g. '127.0.0.1'

    Returns:
        4-byte representation of ip, e.g. b'\x7f\x00\x00\x01'

        :raises ValueError if ip is not a legal IP address.
    """
    try:
        return socket.inet_aton(ip)
    except socket.error:
        raise ValueError(
            "Illegal IP address passed to socket.inet_aton: {0}".format(ip)
        )


def get_max_udp_size() -> int:
    """
    Crazy CTypes magic to do a getsockopt() which determines the max UDP payload size in a platform-agnostic way.

    Returns:
        The maximum length of a UDP packet the current platform supports.
        @rtype:  long
    """
    windows = platform.uname()[0] == "Windows"
    mac = platform.uname()[0] == "Darwin"
    linux = platform.uname()[0] == "Linux"
    lib = None

    if windows:
        sol_socket = ctypes.c_int(0xFFFF)
        sol_max_msg_size = 0x2003
        lib = ctypes.WinDLL("Ws2_32.dll".encode("ascii"))
        opt = ctypes.c_int(sol_max_msg_size)
    elif linux or mac:
        if mac:
            lib = ctypes.cdll.LoadLibrary("libc.dylib")
        elif linux:
            lib = ctypes.cdll.LoadLibrary("libc.so.6")
        sol_socket = ctypes.c_int(socket.SOL_SOCKET)
        opt = ctypes.c_int(socket.SO_SNDBUF)

    else:
        raise Exception("Unknown platform!")

    ulong_size = ctypes.sizeof(ctypes.c_ulong)
    buf = ctypes.create_string_buffer(ulong_size)
    bufsize = ctypes.c_int(ulong_size)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    lib.getsockopt(sock.fileno(), sol_socket, opt, buf, ctypes.pointer(bufsize))

    # Sanity filter against UDP_MAX_PAYLOAD_IPV4_THEORETICAL
    return min(
        ctypes.c_ulong.from_buffer(buf).value,
        ip_constants.UDP_MAX_PAYLOAD_IPV4_THEORETICAL,
    )


def calculate_four_byte_padding(string: str, character: str = "\x00") -> str:
    return character * ((4 - (len(string) & 3)) & 3)


def crc16(string: str, value: int = 0) -> int:
    """CRC-16 poly: p(x) = x**16 + x**15 + x**2 + 1

    Args:
        string (str): Data over which to calculate crc.
        value (int): Initial CRC value.
    """
    crc16_table = []
    for byte in range(256):
        crc = 0

        for _ in range(8):
            if (byte ^ crc) & 1:
                crc = (crc >> 1) ^ 0xA001  # polly
            else:
                crc >>= 1

            byte >>= 1

        crc16_table.append(crc)

    for ch in string:
        value = crc16_table[ord(ch) ^ (value & 0xFF)] ^ (value >> 8)

    return value


def crc32(string: str) -> int:
    return zlib.crc32(string) & 0xFFFFFFFF


def uuid_bin_to_str(uuid: bytes) -> str:
    """Convert a binary UUID to human readable string.

    Args:
        uuid (bytes): Binary UUID.
    """
    (block1, block2, block3) = struct.unpack("<LHH", uuid[:8])
    (block4, block5, block6) = struct.unpack(">HHL", uuid[8:16])

    return "%08x-%04x-%04x-%04x-%04x%08x" % (
        block1,
        block2,
        block3,
        block4,
        block5,
        block6,
    )


def uuid_str_to_bin(uuid: str) -> bytes:
    """Converts a UUID string to binary form.

    Expected string input format is same as uuid_bin_to_str()'s output format.

    Ripped from Core Impacket.

    Args:
        uuid (str): UUID string to convert to bytes.
    """
    uuid_re = r"([\dA-Fa-f]{8})-([\dA-Fa-f]{4})-([\dA-Fa-f]{4})-([\dA-Fa-f]{4})-([\dA-Fa-f]{4})([\dA-Fa-f]{8})"

    matches = re.match(uuid_re, uuid)

    # (uuid1, uuid2, uuid3, uuid4, uuid5, uuid6) = map(lambda x: long(x, 16), matches.groups())
    (uuid1, uuid2, uuid3, uuid4, uuid5, uuid6) = map(
        lambda x: int(x, 16), matches.groups()
    )

    uuid = struct.pack("<LHH", uuid1, uuid2, uuid3)
    uuid += struct.pack(">HHL", uuid4, uuid5, uuid6)

    return uuid


def _ones_complement_sum_carry_16(a: int, b: int) -> int:
    """Compute ones complement sum and carry at 16 bits.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        Sum of a and b, ones complement, carry at 16 bits.
    """
    pre_sum = a + b
    return (pre_sum & 0xFFFF) + (pre_sum >> 16)


def _collate_bytes(msb: str, lsb: str) -> int:
    """
    Helper function for our helper functions.
    Collates msb and lsb into one 16-bit value.

    Args:
        msb (str): Single byte (most significant).
        lsb (str): Single byte (least significant).

    Returns:
        msb and lsb all together in one 16 bit value.
    """
    return (ord(msb) << 8) + ord(lsb)


def ipv4_checksum(msg: bytes) -> int:
    """
    Return IPv4 checksum of msg.

    Args:
        msg (bytes): Message to compute checksum over.

    Returns:
        IPv4 checksum of msg.
    """
    # Pad with 0 byte if needed
    if len(msg) % 2 == 1:
        msg += b"\x00"

    msg_words = map(_collate_bytes, msg[0::2], msg[1::2])
    total = reduce(_ones_complement_sum_carry_16, msg_words, 0)
    return ~total & 0xFFFF


def _udp_checksum_pseudo_header(
    src_addr: bytes, dst_addr: bytes, msg_len: int
) -> bytes:
    """
    Return pseudo-header for UDP checksum.

    Args:
        src_addr (bytes): Source IP address -- 4 bytes.
        dst_addr (bytes): Destination IP address -- 4 bytes.
        msg_len (int): Length of UDP message (not including IPv4 header).

    Returns:
        UDP pseudo-header
    """
    return (
        src_addr
        + dst_addr
        + b"\x00"
        + bytes([ip_constants.IPV4_PROTOCOL_UDP])
        + struct.pack(">H", msg_len)
    )


def udp_checksum(msg: bytes, src_addr: bytes, dst_addr: bytes) -> int:
    """Return UDP checksum of msg.

    Recall that the UDP checksum involves creating a sort of pseudo IP header.
    This header requires the source and destination IP addresses, which this
    function takes as parameters.

    If msg is too big, the checksum is undefined, and this method will
    truncate it for the sake of checksum calculation. Note that this means the
    checksum will be invalid. This loosey goosey error checking is done to
    support fuzz tests which at times generate huge, invalid packets.

    Args:
        msg (str): Message to compute checksum over.
        src_addr (bytes): Source IP address -- 4 bytes.
        dst_addr (bytes): Destination IP address -- 4 bytes.

    Returns:
        UDP checksum of msg.
    """
    # If the packet is too big, the checksum is undefined since len(msg)
    # won't fit into two bytes. So we just pick our best definition.
    # "Truncate" the message as it appears in the checksum.
    msg = msg[0 : ip_constants.UDP_MAX_LENGTH_THEORETICAL]

    return ipv4_checksum(
        _udp_checksum_pseudo_header(src_addr, dst_addr, len(msg)) + msg
    )


def hex_str(s: bytes) -> str:
    """
    Returns a hex-formatted string based on s.

    Args:
        s (bytes): Some string.

    Returns:
        str: Hex-formatted string representing s.
    """
    return " ".join("{:02x}".format(b) for b in bytearray(s))


def pause_for_signal() -> None:
    """
    Pauses the current thread in a way that can still receive signals like SIGINT from Ctrl+C.

    Implementation notes:
     - Linux uses signal.pause()
     - Windows uses a loop that sleeps for 1 ms at a time, allowing signals
       to interrupt the thread fairly quickly.

    Returns:
        None
    """
    try:
        while True:
            signal.pause()
    except AttributeError:
        # signal.pause() is missing for Windows; wait 1ms and loop instead
        while True:
            time.sleep(0.001)


def get_time_stamp() -> str:
    t = time.time()
    s = time.strftime("[%Y-%m-%d %H:%M:%S", time.localtime(t))
    s += ",%03d]" % (t * 1000 % 1000)
    return s


def _indent_all_lines(lines: str, amount: int, ch: str = " ") -> str:
    padding = amount * ch
    return padding + ("\n" + padding).join(lines.split("\n"))


def _indent_after_first_line(lines: str, amount: int, ch: str = " ") -> str:
    padding = amount * ch
    return ("\n" + padding).join(lines.split("\n"))


def format_log_msg(
    msg_type: str = "info",
    description: str = "",
    data: str = "",
    indent_size: int = 2,
    timestamp: str = "",
    format_type: str = "terminal",
):
    if data is None:
        data = b""
    if timestamp is None:
        timestamp = get_time_stamp()

    if description is not None and description != "":
        msg = description
    elif data is not None and len(data) > 0:
        # msg = hex_to_hexstr(input_bytes=data)
        msg = repr_input_bytes(data)
    else:
        msg = ""

    msg = test_step_info[msg_type][format_type].format(msg=msg, n=len(data))
    msg = _indent_all_lines(msg, (test_step_info[msg_type]["indent"]) * indent_size)
    msg = timestamp + " " + _indent_after_first_line(msg, len(timestamp) + 1)

    return msg


def format_msg(
    msg: str, indent_level: int, indent_size: int, timestamp: str = ""
) -> str:
    msg = _indent_all_lines(msg, indent_level * indent_size)
    if timestamp is None:
        timestamp = get_time_stamp()
    return timestamp + " " + _indent_after_first_line(msg, len(timestamp) + 1)


def hex_to_hexstr(input_bytes: bytes = b"") -> str:
    """
    Render input_bytes as ASCII-encoded hex bytes, followed by a best effort
    utf-8 rendering.

    Args:
        input_bytes (bytes): Arbitrary bytes

    Returns:
        str: Printable string
    """
    return hex_str(input_bytes) + " " + repr(input_bytes)


def repr_input_bytes(input_bytes: bytes = b"") -> str:
    if len(input_bytes) > 10000:
        return "[{} bytes]".format(len(input_bytes))
    groups = groupby(input_bytes)
    result = [(label, sum(1 for _ in group)) for label, group in groups]
    b = b""
    hexb = ""
    for c, i in result:
        if i > 10:
            b += "[{}*{}] ".format(chr(c), i).encode()
            hexb += "[{:02x}*{}] ".format(c, i)
        else:
            b += bytes([c] * i)
            hexb += "{:02x} ".format(c)

    return repr(b)
    # return hexb + '- ' + repr(b)


def mkdir_safe(directory_name: str) -> None:
    try:
        os.makedirs(directory_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_all_subclasses(cls: type) -> list:
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def check_sudo() -> bool:
    """
    Check if the current user has root privileges.

    Returns:
        True if the current user has root privileges, False otherwise.
    """
    if os.geteuid() != 0:
        return False
    return True


log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "log")
json_file_path = os.path.join(log_dir, "network_traffic.json")


def log_network_traffic(
    category: str, src_ip: str, dst_ip: str, src_port: int, dst_port: int
) -> None:
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
    }

    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry)

    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=4)
