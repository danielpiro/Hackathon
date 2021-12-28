import socket
import time
import struct
from random import randint
from threading import Thread
import os
from scapy.arch import get_if_addr

os.system("")


# Colors for prints
class Colors:
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    PINK = '\033[35m'


UDP_DEST_IP = '<broadcast>'
UDP_DEST_PORT = 13117
TCP_DEST_PORT = 2006
MESSAGE_LENGTH = 1024
TIME_UNTIL_GAME = 10  # seconds
TIME_TO_PLAY = 10  # seconds
sockUDP = None
sockTCP = None
CONN_A = None
CONN_B = None
counter = 0


def start_udp():
    global sockUDP
    ip = get_if_addr("eth1")
    #ip = "0.0.0.0"
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return ip


def send_broadcast():
    global sockUDP
    ip = start_udp()
    print(Colors.GREEN + "Server started, listening on IP address " + ip)

    while counter < 2:
        buffer = struct.pack('LBH', 0xabcddcba, 0x2, TCP_DEST_PORT)
        sockUDP.sendto(buffer, (UDP_DEST_IP, UDP_DEST_PORT))
        time.sleep(1)  # dont overload


def connect_clients():
    global counter, sockTCP, CONN_B, CONN_A  # can use address later
    while True:
        if counter < 2:  # time.time() < time_out and counter < 2:
            try:
                conn, address = sockTCP.accept()
                if counter == 0:
                    CONN_A = conn
                else:
                    CONN_B = conn

                counter += 1
            except Exception as e:
                pass

        else:
            print(Colors.BLUE + "game starts in 10 secs")
            break


def get_group_names():
    try:
        name_a = CONN_A.recv(MESSAGE_LENGTH).decode()
        name_b = CONN_B.recv(MESSAGE_LENGTH).decode()
        return name_a, name_b, True
    except Exception as e:
        print(Colors.GREEN + "group name was not entered so couldn't start the game")
        send_message("group name was not entered so couldn't start the game")
        return "", "", False


def send_message(message):
    try:
        CONN_A.sendall(message.encode())
        CONN_B.sendall(message.encode())
    except Exception as e:
        pass


def receive_char(answer):
    global CONN_A, CONN_B
    a_won = False
    got_answer = False
    timeout = time.time() + TIME_TO_PLAY

    CONN_A.setblocking(0)
    CONN_B.setblocking(0)
    while time.time() < timeout and not got_answer:
        try:
            data = CONN_A.recv(1024)
            if int(data) == answer:
                a_won = True
            else:
                a_won = False
            got_answer = True
            print(Colors.BLUE + "got data from A, A's answer is " + str(data) + " but the correct answer is " + str(answer))
            return a_won, got_answer
        except Exception as e:
            try:
                data = CONN_B.recv(1024)
                if int(data) == answer:
                    a_won = False
                else:
                    a_won = True
                got_answer = True
                print(Colors.BLUE + "got data from B, B's answer is " + str(data) + " but the correct answer is " + str(answer))

                return a_won, got_answer
            except Exception as e:
                time.sleep(0.1)

    return a_won, got_answer


def send_end_message(name_a, name_b, answer, a_won, got_answer):
    if a_won:
        winner_group = name_a
    else:
        winner_group = name_b
    if got_answer:
        end_message = "Game over!\nThe correct answer was " + str(
            answer) + "!\nCongratulations to the winner:" + winner_group
    else:
        end_message = "Game over!\nNo one answered - Draw"
    print(Colors.PINK + end_message)
    send_message(end_message)


def send_math_question():
    try:
        math = ["2+3", "4-2", "9-3", "2*4", "1*5", "6/3", "8/4", "ln(e^3)"]
        answerTable = [5, 2, 6, 8, 5, 2, 2, 3]
        value = randint(0, 7)
        send_message("How much is: " + math[value] + "?\n")
        return answerTable[value]
    except Exception as e:
        print(e)



def start_game():

    # part 1 - only thing that can stop a game, get group names
    try:
        time.sleep(TIME_UNTIL_GAME)
        name_a, name_b, isValid = get_group_names()
        if isValid:

            # part 2 - send the openning message and random math question
            begin_message = "Welcome to Quick Maths.\nPlayer 1: " + name_a + "\nPlayer 2: " + name_b + "\n====\n Please " \
                                                                                                       "answer the " \
                                                                                                       "following " \
                                                                                                       "question as fast " \
                                                                                                       "as you can:\n "
            send_message(begin_message)
            answer = send_math_question()

            # part 3 - receive answer
            a_won, got_answer = receive_char(answer)

            # part 4 - declare the winner
            send_end_message(name_a, name_b, answer, a_won, got_answer)

    except Exception as e:
        print(e)

def start_tcp():
    global sockTCP
    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init the TCP socket
    sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockTCP.bind(('', TCP_DEST_PORT))
    sockTCP.listen(2)


def reset_params():
    global counter
    counter = 0


def main():

    global counter
    start_tcp()
    while True:
        try:
            time.sleep(1)  # not a must, but make sure clients can disconnect

            # part 1 - broadcast
            broadcaster = Thread(target=send_broadcast, args=())

            # part 2 - wait for 2 clients to connect, wait indefinitely
            client_connector = Thread(target=connect_clients, args=())
            broadcaster.start()
            client_connector.start()

            # part 3 - make sure they finish before game starts
            broadcaster.join()
            client_connector.join()

            # part 4 - play the game
            start_game()

            # part 5 - game ended, start anew
            reset_params()

            CONN_A.close()
            CONN_B.close()
        except Exception as e:
            pass
        print("Game over, sending out offer requests...")


if __name__ == "__main__":
    main()
