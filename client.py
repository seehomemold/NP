import socket
#Host = "3.87.28.92"

Port = 3110

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('',Port))
