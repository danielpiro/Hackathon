import socket
import time
import struct
from random import randint
from threading import Thread
import os

os.system("")


# Group of Different functions for different styles
class Colors:
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    RESET = '\033[0m'


UDP_DEST_IP = '<broadcast>'
UDP_DEST_PORT = 13117
TCP_DEST_PORT = 2006
MESSAGE_LENGTH = 1024
TIME_UNTIL_GAME = 10  # seconds
TIME_TO_PLAY = 10  # seconds
sockUDP = None
sockTCP = None
NAME_A = ''
NAME_B = ''
CONN_A = None
CONN_B = None
A_WON = False
counter = 0
amountOfPlayers = 2
answer = -1
gotAnswer = False


def start_udp():
    global sockUDP
    #ip = get_if_addr("eth1")
    ip = "0.0.0.0"
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return ip


def send_broadcast():
    global sockUDP
    ip = start_udp()
    print(Colors.GREEN + "Server started, listening on IP address " + ip)


    while counter < amountOfPlayers:
            buffer = struct.pack('LBH', 0xabcddcba, 0x2, TCP_DEST_PORT)
            sockUDP.sendto(buffer, (UDP_DEST_IP, UDP_DEST_PORT))
            time.sleep(1)  # dont overload



def connect_clients():
    global counter, sockTCP,CONN_B, CONN_A # can use address later
    while True:
        if counter < amountOfPlayers:  # time.time() < time_out and counter < 2:
            try:
                conn, address = sockTCP.accept()

                if counter == 0:
                    CONN_A = conn
                    #print(Colors.BLUE + "connected new client 1 ")
                else:
                    CONN_B = conn
                    #print(Colors.MAGENTA + "connected new client 2 ")

                counter += 1
                # print( Colors.GREEN + "New player connected with ip: " + address[0] + " and with port " + str(address[1]))
            except Exception as e:
                pass

        else:
            print(Colors.BLUE + "game starts in 10 secs")
            time.sleep(TIME_UNTIL_GAME)
            break


def get_group_names():
    global NAME_A, NAME_B
    try:
        NAME_A = CONN_A.recv(MESSAGE_LENGTH).decode()
        NAME_B = CONN_B.recv(MESSAGE_LENGTH).decode()
        return True
    except Exception as e:
        print(Colors.GREEN + "group name was not entered so couldn't start the game")
        send_message("group name was not entered so couldn't start the game");
        return False



def send_message(message):
    try:
        CONN_A.sendall(message.encode())
        CONN_B.sendall(message.encode())
    except Exception as e:
        pass


def receive_char():
    global A_WON, gotAnswer, CONN_A, CONN_B

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
            print(Colors.BLUE + "got data from A, A's answer is " + str(data) + " but the real answer is " + str(answer))
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



def send_end_message():
    if A_WON:
        winner_group = NAME_A
    else:
        winner_group = NAME_B

    if gotAnswer:
        end_message = "Game over!\nThe correct answer was " + str(
            answer) + "!\nCongratulations to the winner:" + winner_group
    else:
        end_message = "Game over!\nNo one answered - Draw"
    print(Colors.MAGENTA + end_message)
    send_message(end_message)



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

    #part 1- only thing that can stop a game, get group names
    if (get_group_names()):

        #part 2 - send the openning message and random math question
        begin_message = "Welcome to Quick Maths.\nPlayer 1: " + NAME_A + "\nPlayer 2: " + NAME_B + "\n====\n Please answer the following question as fast as you can:\n"
        send_message(begin_message)
        send_math_question()

        #part 3 - recieve answer
        receive_char()

        #part 4 - declare the winner
        send_end_message()



def start_tcp():
    global sockTCP
    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init the TCP socket
    sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockTCP.bind(('', TCP_DEST_PORT))
    sockTCP.listen(2)


def main():
    global counter,A_WON,gotAnswer,answer
    start_tcp()
    while True:


        time.sleep(1)  # not a must, but make sure clients can disconnect

        # part 1 - broadcast
        broadcaster = Thread(target=send_broadcast, args=())

        #part 2 - wait for 2 clients to connect, wait indefinetly
        client_connector = Thread(target=connect_clients, args=())

        broadcaster.start()
        client_connector.start()

        #part 3 - make sure they finish before game starts
        broadcaster.join()
        client_connector.join()

        #part 4 - play the game
        start_game()

        #part 5 - game ended, start anew

        counter = 0
        A_WON = False
        gotAnswer = False
        answer = -1
        try:
            CONN_A.close()
            CONN_B.close()
        except:
            pass
        print("Game over, sending out offer requests...")

if __name__ == "__main__":
    main()
