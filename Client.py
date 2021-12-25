import os
import socket
import struct
import time
from threading import Thread
from termcolor import colored

os.system("")

UDP_PORT = 13117
MESSAGE_LEN = 1024
GAME_TIME = 10
BROADCAST_IP = ""
sockUDP = None
sockTCP = None
printBool = True
end = time.time()


# Handle signal to escape blocking thread
def handler(signum, frame):
    raise Exception()


def print_server_message():
    while printBool:
        time.sleep(0.1)
        try:
            data = sockTCP.recv(MESSAGE_LEN).decode()
            print(colored(data, 'green'))
        except Exception as e:
            print(e)
            break


print(colored("Client started, listening for offer requests...", 'green'))  # waits for server suggestion


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


while True:
    ip, message = start_udp()
    try:
        printBool = True
        cookie, msg_type, tcp_port = struct.unpack('LBH', message)  # get message in specific format
        if cookie == 0xabcddcba and msg_type == 0x2:  # check if message is as expected
            print(colored("Received offer from " + ip + " attempting to connect...", 'green'))
            start_tcp(ip, tcp_port)
            group_name = input('Enter your group name: ')
            print(group_name)
            # it will wait in socket until server recv it
            sockTCP.sendall(group_name.encode())  # send team's name to server
            msg = sockTCP.recv(MESSAGE_LEN).decode()
            print(colored(msg, 'pink'))
            msg2 = sockTCP.recv(MESSAGE_LEN).decode()
            print(colored(msg2, 'pink'))  # math question
            assign_thread()  # end game
            while True:
                try:
                    ch = input("enter char answer")
                    print(ch)
                    sockTCP.sendall(ch.encode())  # if socket is still open, send it
                    time.sleep(0.2)  # wait for server to answer
                    printBool = False
                    break
                except Exception as e:
                    print(e)
                    break

        else:
            print(colored("Bad UDP Message Format", 'red'))  # got message not in the expected format
    except Exception as e:
        print(colored(str(e), 'red'))
