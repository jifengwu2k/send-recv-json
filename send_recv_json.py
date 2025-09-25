# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from json import loads, dumps
from struct import pack, unpack

from typing import Any, Callable

if sys.version_info < (3,):
    def dump_json_to_ascii_bytes(json):
        # type: (Any) -> bytes
        return dumps(json, ensure_ascii=True)


    def load_json_from_ascii_bytes(ascii_bytes):
        # type: (bytes) -> Any
        return loads(ascii_bytes)
else:
    def dump_json_to_ascii_bytes(json):
        # type: (Any) -> bytes
        return dumps(json, ensure_ascii=True).encode('ascii')


    def load_json_from_ascii_bytes(ascii_bytes):
        # type: (bytes) -> Any
        return loads(ascii_bytes.decode('ascii'))


def send_all(send, data):
    # type: (Callable[[bytes], int], bytes) -> int
    sent = 0
    while sent < len(data):
        n = send(data[sent:])
        if n <= 0:
            raise IOError('Expected to send %d bytes, sent %d bytes. Cannot send anymore.' % (len(data), sent))
        sent += n
    return sent


def recv_all(recv, n):
    # type: (Callable[[int], bytes], int) -> bytes
    data = bytearray()
    while len(data) < n:
        more = recv(n - len(data))
        if not more:
            raise EOFError("Expected to recv %d bytes, recv'd %d bytes. Cannot recvany more." % (n, len(data)))
        data.extend(more)
    return bytes(data)


def send_json(send, json):
    # type: (Callable[[bytes], int], Any) -> int
    serialized = dump_json_to_ascii_bytes(json)

    # `!` - Network byte order (big-endian)
    # `I` - Unsigned integer (4 bytes, range: 0 to 4294967295)
    header = pack('!I', len(serialized))

    return send_all(send, header) + send_all(send, serialized)


def recv_json(recv):
    # type: (Callable[[int], bytes]) -> Any
    header = recv_all(recv, 4)
    length, = unpack('!I', header)
    serialized = recv_all(recv, length)

    return load_json_from_ascii_bytes(serialized)
