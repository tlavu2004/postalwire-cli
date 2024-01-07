import socket

def send(sender: socket, msg):
    sender.sendall((msg))

def recv(receiver, size):
    res = ""
    while (len(res) < size):
        res += receiver.recv(100000).decode()
    return res