import struct
import sys
from typing import List

from pythonping import icmp, network


def hex_to_bytes(hex_str: str) -> List[int]:
    return list(bytearray.fromhex(hex_str))


def packet_to_str(packet: icmp.ICMP) -> str:
    result = (
        f"ICMP packet, type: {packet.message_type}, code: {packet.message_code}, "
        + f"checksum: {packet.received_checksum}, id: {packet.id}, "
        + f"seq: {packet.sequence_number}, payload: {packet.payload} "
    )

    if packet.received_checksum == packet.expected_checksum:
        result += "(correct checksum)"
    else:
        result += f"(incorrect checksum, expected: {packet.expected_checksum})"

    return result


if __name__ == "__main__":
    with open(sys.argv[1], "r") as inp_file:
        hex_input = inp_file.read()

    bytes_input = bytes(bytearray.fromhex(hex_input))

    request = icmp.ICMP()
    (
        request.message_type,
        request.message_code,
        request.received_checksum,
        request.id,
        request.sequence_number,
    ) = struct.unpack("BBHHH", bytes_input[0:8])
    request.payload = bytes_input[8:]

    print(f"Request:  {packet_to_str(request)}")

    print(f"Sending request.")
    socket = network.Socket("localhost", "icmp", source="localhost")
    socket.send(bytes_input)

    print(f"Listening for responses.")
    time_left = 2
    while time_left > 0:
        raw_packet, source_socket, time_left = socket.receive(time_left)
        print(f"Received response {raw_packet}")

        if not raw_packet:
            continue

        response = icmp.ICMP()
        response.unpack(raw_packet)

        if (
            response.id == request.id
            and response.message_type == icmp.Types.EchoReply.type_id
        ):
            payload_matched = request.payload == response.payload

            print(f"Response: {packet_to_str(response)}")

            if payload_matched:
                print(f"Payload matched.")
            else:
                print(f"Payload did not match.")

            break
        else:
            print(f"Response to different request.")
    else:
        print(f"Timeout.")
