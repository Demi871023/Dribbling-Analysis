import socket
import cv2
from threading import Thread

import Configs
import ImageRecognizer as Recognizer
import VisualAttention as Attention


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def recv_socket():
    while True:
        message = str(conn.recv(1024), encoding='utf-8')
        print(message)

        mess = message.split(",")

        if mess[0] == "SET":
            if mess[1] == "Unmovable":
                Configs.user_choosen_mode = Configs.MODE_UNMOVABLE
            if mess[1] == "Movable":
                Configs.user_choosen_mode = Configs.MODE_MOVABLE
            if mess[2] == "Disable":
                Configs.user_choosen_opponent = Configs.OPPONENT_DISABLE
            if mess[2] == "Enable":
                Configs.user_choosen_opponent = Configs.OPPONENT_ENABLE
            if mess[3] == "NumberAdd":
                Configs.user_choosen_task = Configs.TASK_NUMBERADD
            if mess[3] == "ColorChange":
                Configs.user_choosen_task = Configs.TASK_COLORCHANGE
            if mess[4] == "POUND":
                Configs.user_choosen_dribbling = Configs.DRIBBLING_POUND
            if mess[4] == "CROSSOVER":
                Configs.user_choosen_dribbling = Configs.DRIBBLING_CROSSOVER
            if mess[4] == "ONESIDELEG":
                Configs.user_choosen_dribbling = Configs.DRIBBLING_ONESIDELEG
            if mess[4] == "BEHIND":
                Configs.user_choosen_dribbling = Configs.DRIBBLING_BEHIND

            print("=== USER SETTING ===")
            print(Configs.user_choosen_mode)
            print(Configs.user_choosen_opponent)
            print(Configs.user_choosen_task)
            print(Configs.user_choosen_dribbling)
            print("=== USER SETTING ===")

        if mess[0] == "STATE":
            if mess[1] == "Start":
                training_state = Configs.STATE_START
            if mess[1] == "Pause":
                training_state = Configs.STATE_PAUSE
            if mess[2] == "Finish":
                training_state = Configs.STATE_FINISH

        if mess[0] == "CONNECT":
            if mess[1] == "Hello":
                print("Connect Successful...")
            if mess[1] == "Bye":
                Configs.connect_state = Configs.CONNECT_STATE_BYE
                # thread_visual_attention.join()
                print("Disconnected...")
                break

def run_socket():
    global conn
    global addr

    global TASK_SETTING, DRIBBLING_SETTING
    
    conn, addr = server.accept()
    greet_recvmessage = str(conn.recv(1024), encoding='utf-8')
    greet_sendmessage = "Connect Successfully"
    conn.sendall(greet_sendmessage.encode())
    print(greet_recvmessage)

    Configs.connect_state = Configs.CONNECT_STATE_HELLO

    thread_recv = Thread(target=recv_socket, args=(), daemon=True)
    thread_recv.start()

    while True:

        if Configs.connect_state == Configs.CONNECT_STATE_BYE:
            break

        if Configs.training_state == Configs.STATE_PAUSE:
            sendmessage = "TRAINING PAUSE"
            conn.sendall(sendmessage.encode())
        if Configs.training_state == Configs.STATE_START:
            sendmessage = "TRAINING START"
            conn.sendall(sendmessage.encode())



def initial_socket():
    server.bind((Configs.SERVER_HOST, Configs.SERVER_PORT))
    server.listen(Configs.LISTEN_NUM)
    print(" *** SERVER START *** ")

def initial_image_recognizer():
    Recognizer.image_recognizer_main()


if __name__ == "__main__":

    # Initialize sock and recognizer module
    initial_socket()
    initial_image_recognizer()

    if Configs.RECOGNIZER_MODE == "IMAGE":

        thread_socket = Thread(target=run_socket, args=(), daemon=True)
        thread_image_recognizer = Thread(target = Recognizer.inference, args = (), daemon = True)
        thread_image_visualize = Thread(target= Recognizer.visualize, args = (), daemon = True)
        thread_socket.start()
        thread_image_visualize.start()
        thread_image_recognizer.start()
        thread_image_recognizer.join()
        thread_image_visualize.join()

        conn.close()    # Disconnected...

        thread_visual_attention = Thread(target = Attention.attention_main, args = (), daemon = True)
        thread_visual_attention.start()
        thread_visual_attention.join()

    if Configs.RECOGNIZER_MODE == "IMU":
        pass

    if Configs.RECOGNIZER_MODE == "BOTH":
        pass
