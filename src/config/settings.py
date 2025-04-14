"""
Settings for the Chad replay service.

GENERAL_SETTINGS:
    Attributes:
        use_rich_tables (bool): Whether to use rich tables or not.
        color_supported (bool): Whether the terminal supports colors or not.

LOGGER_SETTINGS:
    Attributes:
        color_log_file (bool): Whether to color the log file or not.

NETWORK_SETTINGS:
    Attributes:
        interface (str): The network interface to listen on.
        display_filter (str): The display filter to apply to the packets.
        bpf_filter (str): The BPF filter to apply to the packets.
        loop (bool): Whether to loop the packets or not.
        packet_count (int): The number of packets to capture.
"""


class GENERAL_SETTINGS:
    use_rich_tables = True
    color_supported = True


class LOGGER_SETTINGS:
    color_log_file = True


class NETWORK_SETTINGS:
    interface = "eth0"
    display_filter = None
    bpf_filter = ""
    loop = None
    packet_count = 80
    ip_address = "192.168.56.1"
