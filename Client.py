import os
import socket
import struct
import sys
import select

os.system("")

UDP_PORT = 13117
MESSAGE_LEN = 1024
GAME_TIME = 10
sockUDP = None
sockTCP = None


# Colors for prints
class Colors:
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    PINK = '\033[35m'


def printMessageOrRead():
    # wait for read or write from client or server
    readers, _, _ = select.select([sys.stdin, sockTCP], [], [])
    for reader in readers:
        if reader is sockTCP:
            data = sockTCP.recv(MESSAGE_LEN).decode()
            print(Colors.PINK + data)
        else:
            ch = sys.stdin.read(1)
            sockTCP.sendall(ch.encode())
            printMessageOrRead()  # because will need to print server answer


def start_udp():
    global sockUDP
    # create UDP socket with the variables we need
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # init UDP socket
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sockUDP.bind(("", UDP_PORT))
    # assume server started and need to connect
    message, location = sockUDP.recvfrom(MESSAGE_LEN)
    server_ip_address = str(location[0])
    return server_ip_address, message


def start_tcp(ip, tcp_port):
    global sockTCP
    # create custom TCP socket
    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockTCP.connect((ip, tcp_port))


def print_start(first_print):
    if first_print == 0:
        print(Colors.GREEN + "Client started, listening for offer requests...")


first_print = 0
while True:
    print_start(first_print)
    first_print += 1
    # waits for server suggestion
    # part 1 get udp message
    ip, message = start_udp()
    try:
        # part 2 connect to server
        printBool = True
        cookie, msg_type, tcp_port = struct.unpack('LBH', message)
        # part 3 make sure it's the correct server
        if cookie == 0xabcddcba and msg_type == 0x2:  # check if message is as expected
            print(Colors.GREEN + "Received offer from " + ip + " attempting to connect...")
            start_tcp(ip, tcp_port)
            # part 4 start game with group name
            group_name = input(Colors.PINK + 'Enter your group name: ')
            sockTCP.sendall(group_name.encode())  # send team's name to server
            # part 5 start game
            print(sockTCP.recv(MESSAGE_LEN).decode())  # the game begin message
            print(sockTCP.recv(MESSAGE_LEN).decode())  # math question
            # part 6 play game, win or lost
            printMessageOrRead()
            print(Colors.BLUE + "Server disconnected, listening for offer requests...")
            first_print = 0
        else:
            print(Colors.GREEN + "Bad UDP Message Format")
            # got message not in the expected format
    except Exception as e:
        pass
