#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re

# you may use urllib to encode data appropriately
from urllib.parse import urlparse as parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):

    def getIp(self, host):
        print(f" ip for: {host} is {socket.gethostbyname(host)}")

        return socket.gethostbyname(host)

    def connect(self, host, port):
        # print("\n\n+++++++++++++++++", "bruhhhhhhh", "++++++++++++++++++++++\n\n")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None


    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part

        return buffer.decode("utf-8")

    def GET(self, url, args=None):

        parsed = parse(url)

        port = parsed.netloc.split(":")
        # print(int(port[1]) if (len(port) == 2 and port[1] != "") else 80)
        self.connect(
            parsed.netloc.split(":")[0],
            int(port[1]) if (len(port) == 2 and port[1] != "") else 80,
        )

        path = (parsed.path + "/").replace("//", "/")
        # print("\n\n+++++++++++++++++", path, parsed.path, "++++++++++++++++++++++\n\n")
        # print(
        #     "\r\n".join(
        #         [
        #             f"GET {path} HTTP/1.1",
        #             f"Host: {parsed.netloc}",
        #             "Connection: close",
        #             "\r\n",
        #         ]
        #     )
        # )
        self.sendall(
            "\r\n".join(
                [
                    f"GET {path} HTTP/1.1",
                    f"Host: {parsed.netloc}",
                    "Connection: close",
                    "\r\n",
                ]
            )
        )

        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)
        self.socket.close()
        if not data:
            return HTTPResponse(400, "")

        header, body = data.split("\r\n\r\n")
        # print(header)
        # print(header, body)

        code = int(header.split("\n")[0].split(" ")[1])
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed = parse(url)
        port = parsed.netloc.split(":")
        self.connect(
            parsed.netloc.split(":")[0],
            int(port[1]) if (len(port) == 2 and port[1] != "") else 80,
        )

        content = ""

        assert type(args) is str or type(args) is dict or args is None

        if type(args) is str:
            content = args
        elif args is not None:
            items = []
            for key, val in args.items():
                items.append(f"{key}={val}")
            content = "&".join(items)

        # print(
        #     "\r\n".join(
        #         [
        #             f"POST {parsed.path} HTTP/1.1",
        #             f"Host: {parsed.netloc}",
        #             "Content-Type: application/x-www-form-urlencoded",
        #             "Connection: close",
        #             "\r\n",
        #             content,
        #         ]
        #     )
        # )

        self.sendall(
            "\r\n".join(
                [
                    f"POST {parsed.path} HTTP/1.1",
                    f"Host: {parsed.netloc}",
                    "Content-Type: application/x-www-form-urlencoded",
                    f"Content-Length: {len(content)}",
                    "Connection: close",
                    "\r\n" + content,
                ]
            )
        )
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)
        self.socket.close()
        header, body = data.split("\r\n\r\n")

        # print(header, body)

        code = int(header.split("\n")[0].split(" ")[1])
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()

    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(
            client.command(url=sys.argv[2], args=sys.argv[1], command="POST"),
        )
    else:
        print(client.command(sys.argv[1]))
