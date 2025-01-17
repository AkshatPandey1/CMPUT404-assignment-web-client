#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Akshat Pandey (apandey3)
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
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")
    print("GET example: httpclient.py GET http://www.google.com\n")
    print("POST example: httpclient.py POST http://www.google.com \"{'name':'value'}\"\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split(" ")[1])

    def get_body(self, response):
        return response.split("\r\n")[-1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
    # read everything from the socket

    def close(self):
        self.socket.close()

    def GET(self, url, args=None):
        # Parse url
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 80
        path = urllib.parse.quote(parsed_url.path) or "/"  # To handle spaces in path names

        # Create request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n"
        request += "\r\n\r\n"

        # If args are passed, add them to the request
        if args:
            request += urllib.parse.urlencode(args)

        # Connect to server
        self.connect(host, port)

        # Send request
        self.sendall(request)

        # Receive response
        response = self.recvall(self.socket)

        # Close connection
        self.close()

        # Parse response
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def POST(self, url, args=None):
        # Parse url
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 80
        path = urllib.parse.quote(parsed_url.path) or "/"

        # Create request
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"

        print(request)

        # If args are passed, add them to the request
        if args:
            request += f"Content-Length: {len(urllib.parse.urlencode(args))}\r\n"
            request += "\r\n"
            request += urllib.parse.urlencode(args)
        else:
            request += "Content-Length: 0\r\n"
            request += "\r\n\r\n"

        # Connect to server
        self.connect(host, port)

        # Send request
        self.sendall(request)

        # Receive response
        response = self.recvall(self.socket)

        # Close connection
        self.close()

        # Parse response
        code = self.get_code(response)
        body = self.get_body(response)
        print(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    elif (len(sys.argv) == 4):  # Allows user to pass in args as a dict
        sys.argv[3] = eval(sys.argv[3])
        print(client.command(sys.argv[2], sys.argv[1], sys.argv[3]))
    else:
        print(client.command(sys.argv[1]))
