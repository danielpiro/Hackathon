import socket
import time
import struct
from random import randint
from threading import Thread
import os

# from scapy.arch import get_if_addr

os.system("")


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


UDP_DEST_IP = '<broadcast>'
UDP_DEST_PORT = 13117
TCP_DEST_PORT = 2006
MESSAGE_LENGTH = 1024
TIME_TO_CONNECT = 10  # seconds
TIME_TO_PLAY = 10  # seconds
sockUDP = None
sockTCP = None
IP_A = ''
IP_B = ''
PORT_A = ''
PORT_B = ''
NAME_A = ''
NAME_B = ''
CONN_A = None
CONN_B = None
A_WON = False
counter = 0
amountOfPlayers= 1
answer = -1
gotAnswer = False


def start_udp():
    global sockUDP
    # ip = get_if_addr("eth1")
    ip = "0.0.0.0"
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return ip


def send_broadcast():
    global sockUDP
    ip = start_udp()
    print("Server started, listening on IP address " + ip)
    time_out = time.time() + TIME_TO_CONNECT  # the time to wait for players
    while True:
        if counter<amountOfPlayers:             # time.time() < time_out:
            buffer = struct.pack('LBH', 0xabcddcba, 0x2, TCP_DEST_PORT)
            sockUDP.sendto(buffer, (UDP_DEST_IP, UDP_DEST_PORT))
            time.sleep(0.5)  # wait 1 sec
        else:
            break


def connect_clients():
    global counter, sockTCP, IP_A, PORT_A, CONN_A, IP_B, PORT_B, CONN_B
    time_out = time.time() + TIME_TO_CONNECT  # the time to wait for players
    sockTCP.settimeout(TIME_TO_CONNECT)
    while True:
        if counter<amountOfPlayers:                 #time.time() < time_out and counter < 2:
            try:
                conn, address = sockTCP.accept()

                if counter == 0:
                    IP_A = address[0]
                    PORT_A = address[1]
                    CONN_A = conn
                    print ("connected new client 1 " + IP_A)
                else:
                    IP_B = address[0]
                    PORT_B = address[1]
                    CONN_B = conn
                    print ("connected new client 2 " + IP_A)

                counter += 1
                print("New player connected with ip: " + address[0] + " and with port " + str (address[1]))
            except Exception as e:
                pass

        else:
            print("game starts in 10 secs")
            time.sleep(TIME_TO_PLAY)
            break


def get_group_names():
    global NAME_A, NAME_B
    try:
        NAME_A = CONN_A.recv(MESSAGE_LENGTH).decode()
        print(NAME_A)
        NAME_B = CONN_B.recv(MESSAGE_LENGTH).decode()
        print (NAME_B)
    except Exception as e:
        print ("group name was not entered so could'nt start the game")


def send_message_to_group(message, group):
    for key in group.keys():
        try:
            key.sendall(message)
        except Exception as e:
            pass


def send_message(message):
    try:
        CONN_A.sendall(message.encode())
        CONN_B.sendall(message.encode())
    except Exception as e:
        pass


def receive_char():
    global A_WON, gotAnswer,CONN_A,CONN_B
    #CONN_A.setblocking(0)
    #CONN_B.setblocking(0)
    gotAnswer = False
    timeout = time.time() + TIME_TO_PLAY
    while time.time() < timeout and gotAnswer == False:
        try:

            data = CONN_A.recv(1024)

            if int(data) == answer:
                A_WON = True
            else:
                A_WON = False
            gotAnswer = True
            print("got data from A, A's answer is " + str(data) + " but the real answer is " + str(answer))
        except:
            try:
                data = CONN_B.recv(1024)
                if int(data) == answer:
                    A_WON = False
                else:
                    A_WON = True
                gotAnswer = True

            except:
                time.sleep(0.1)



def total_messages(group):
    m = ""
    for c in group.keys():
        try:
            c.settimeout(0)
            m += c.recv(MESSAGE_LENGTH).decode()
        except Exception as e:
            pass
    return m


def send_end_message():
    winner_group = ''
    if A_WON:
        winner_group = NAME_A
    else:
        winner_group = "No Name"  # NAME_B

    if gotAnswer:
        end_message = "Game over!\nThe correct answer was " + str(answer) + "!\nCongratulations to the winner:" + winner_group
    else:
        end_message = "Game over!\nNo one answered - Draw"
    print (end_message)
    send_message(end_message)


"""
method: start_game
purpose: play the game
"""


def send_math_question():
    global answer
    math = {}
    answerTable = {}
    math[0] = "2+3"
    math[1] = "4-2"
    math[2] = "9-3"
    math[3] = "2*4"
    math[4] = "1*5"
    math[5] = "6/3"
    math[6] = "8/4"
    math[7] = "ln(e^3)"
    answerTable[0] = 5
    answerTable[1] = 2
    answerTable[2] = 6
    answerTable[3] = 8
    answerTable[4] = 5
    answerTable[5] = 2
    answerTable[6] = 2
    answerTable[7] = 3

    value = randint(0, 7)
    send_message("How much is: " + math[value] + "?\n")
    answer = answerTable[value]


def start_game():

    get_group_names()
    begin_message = "Welcome to Quick Maths.\nPlayer 1: "+ NAME_A + "\nPlayer 2: " + NAME_B +"\n====\n Please answer the following question as fast as you can:\n"

    send_message(begin_message)
    send_math_question()
    receive_char()
    send_end_message()


def start_tcp():
    global sockTCP
    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init the TCP socket
    sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockTCP.bind(('', TCP_DEST_PORT))
    sockTCP.listen(2)


def main():
    global counter
    start_tcp()
    connections = {}
    while True:
        time.sleep(1)  # reduce CPU preformence
        broadcaster = Thread(target=send_broadcast, args=())  # send broadcast for players
        client_connector = Thread(target=connect_clients, args=())  # accepts new players
        broadcaster.start()
        client_connector.start()
        broadcaster.join()
        client_connector.join()
        start_game()  # play the game
        print("Starting new Game, sending out offer requests...")  # game session over
        counter = 0
        A_WON=False
        gotAnswer=False
        answer=-1
        try:
            CONN_A.close()
            CONN_B.close()
        except:
            pass



if __name__ == "__main__":
    main()
