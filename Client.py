import os
import signal
import socket
import struct
import time
from threading import Thread

# import getch

os.system("")

UDP_PORT = 13117
MESSAGE_LEN = 1024
GAME_TIME = 10  # seconds
BROADCAST_IP = ""
sockUDP = None
sockTCP = None
printBool = True

end = time.time()


# Group of Different functions for different styles
class style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


# Handle signal to escape blocking thread
def handler(signum, frame):
    raise Exception()


def print_server_message():
    while printBool:
        time.sleep(0.1)
        try:
            data = sockTCP.recv(MESSAGE_LEN).decode()
            print(data)
        except:
            break


print("Client started, listening for offer requests...")  # waits for server suggestion


def start_udp():
    global sockUDP
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # init UDP socket
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockUDP.bind((BROADCAST_IP, UDP_PORT))
    message, location = sockUDP.recvfrom(MESSAGE_LEN)
    server_ip_address = str(location[0])
    return server_ip_address, message


def start_tcp(ip='127.0.0.1', tcp_port='2004'):
    global sockTCP
    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init TCP socket
    sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockTCP.connect((ip, tcp_port))


def assign_thread():
    printer = Thread(target=print_server_message, args=())
    printer.start()
    # signal.signal(signal.SIGALRM, handler)
    # signal.alarm(GAME_TIME)


while True:
    ip, message = start_udp()
    try:
        printBool = True
        cookie, msg_type, tcp_port = struct.unpack('LBH', message)  # get message in specific format
        if cookie == 0xabcddcba and msg_type == 0x2:  # check if message is as expected
            print("Received offer from " + ip + " attempting to connect...")
            start_tcp(ip, tcp_port)
            group_name = input('Enter your group name: ')
            print(group_name)
            # it will wait in socket until server recv it
            sockTCP.sendall(group_name.encode())  # send team's name to server
            print(sockTCP.recv(MESSAGE_LEN).decode())  # the game begin message
            print(sockTCP.recv(MESSAGE_LEN).decode())  # math question
            assign_thread()  # end game
            while True:
                try:
                    # ch = getch.getch().encode()  # blocking, wait for char
                    ch = input("enter char answer")

                    print(ch)
                    sockTCP.sendall(ch.encode())  # if socket is still open, send it
                    time.sleep(0.2)  # wait for server to answer
                    printBool = False
                    break
                except Exception as e:
                    break

        else:
            print("Bad UDP Message Format")  # got message not in the expected format
    except Exception as e:
        print(e)
