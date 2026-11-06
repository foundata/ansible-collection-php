#!/usr/bin/python3
# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Request the PHP runtime fixture through the test pool's FastCGI socket."""

import socket
import struct


def record(kind, body=b""):
    """Encode a FastCGI record for request 1."""
    return struct.pack("!BBHHBB", 1, kind, 1, len(body), 0, 0) + body


def read_exact(connection, length):
    """Read one complete field or fail on a truncated response."""
    data = b""
    while len(data) < length:
        chunk = connection.recv(length - len(data))
        if not chunk:
            raise RuntimeError("FPM closed an incomplete FastCGI response")
        data += chunk
    return data


def main():
    """Print the response body; fail on FastCGI or PHP errors."""
    parameters = {
        b"REQUEST_METHOD": b"GET",
        b"SCRIPT_FILENAME": b"/var/tmp/foundata-php-runtime.php",
    }
    encoded = b"".join(
        bytes((len(key), len(value))) + key + value for key, value in parameters.items()
    )
    output = b""
    errors = b""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(10)
        connection.connect("/run/php-fpm-testpool.sock")
        connection.sendall(
            record(1, struct.pack("!HB5x", 1, 0))
            + record(4, encoded)
            + record(4)
            + record(5)
        )
        while True:
            version, kind, request, length, padding, _reserved = struct.unpack(
                "!BBHHBB", read_exact(connection, 8)
            )
            if version != 1 or request != 1:
                raise RuntimeError("Unexpected FastCGI response")
            body = read_exact(connection, length)
            read_exact(connection, padding)
            if kind == 6:
                output += body
            elif kind == 7:
                errors += body
            elif kind == 3:
                if struct.unpack("!IB3x", body) != (0, 0):
                    raise RuntimeError("FastCGI request failed")
                break
    if errors:
        raise RuntimeError(errors.decode())
    headers, separator, body = output.partition(b"\r\n\r\n")
    if not separator or b"Status:" in headers:
        raise RuntimeError("Invalid HTTP response from FPM")
    print(body.decode())


if __name__ == "__main__":
    main()
