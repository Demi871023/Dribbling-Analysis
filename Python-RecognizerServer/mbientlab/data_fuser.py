# usage: python data_fuser.py [mac1] [mac2] ... [mac(n)]
from __future__ import print_function
from ctypes import c_void_p, cast, POINTER
from mbientlab.metawear import MetaWear, libmetawear, parse_value, cbindings
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event, Thread
from sys import argv
import time
import threading
import datetime
import socket
import json
import cv2
import os

global states
states = []
ENABLE_MAG = False
savingState = False
IDLabel = 0
IMUdir = 0
IMGdir = 0


class State:
    # init
    def __init__(self, device):
        self.device = device
        self.callback = cbindings.FnVoid_VoidP_DataP(self.data_handler)
        self.processor = None
        self.packets = []

    # download data callback fxn
    def data_handler(self, ctx, data):
        if ENABLE_MAG :
            values = parse_value(data, n_elem = 3)
            print("Time(ms): %d, Address: %s, acc: (%.4f,%.4f,%.4f), gyro: (%.4f,%.4f,%.4f), mag: (%.4f,%.4f,%.4f)" % (data.contents.epoch, self.device.address, values[0].x, values[0].y, values[0].z, values[1].x, values[1].y, values[1].z, values[2].x, values[2].y, values[2].z))
        else :
            values = parse_value(data, n_elem = 2)
            #print("Time(ms): %d, Address: %s, acc: (%.4f,%.4f,%.4f), gyro: (%.4f,%.4f,%.4f)" % (data.contents.epoch, self.device.address, values[0].x, values[0].y, values[0].z, values[1].x, values[1].y, values[1].z))
            #print("Time(ms): %d, Address: %s, acc: (%s), gyro: (%.4f,%.4f,%.4f)" % (data.contents.epoch, self.device.address, values[0], values[1].x, values[1].y, values[1].z))
            self.packets.append("%.4f %.4f %.4f %.4f %.4f %.4f" % (values[0].x, values[0].y, values[0].z, values[1].x, values[1].y, values[1].z))

    # setup
    def setup(self):
        # ble settings
        libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
        sleep(1.5)
        # events
        e = Event()
        # processor callback fxn
        def processor_created(context, pointer):
            self.processor = pointer
            e.set()
        # processor fxn ptr
        fn_wrapper = cbindings.FnVoid_VoidP_VoidP(processor_created)

        libmetawear.mbl_mw_acc_bmi270_set_odr(self.device.board, AccBmi270Odr._100Hz) # BMI 270 specific call
        libmetawear.mbl_mw_acc_bosch_set_range(self.device.board, AccBoschRange._16G)
        libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)
        
        libmetawear.mbl_mw_gyro_bmi270_set_range(self.device.board, GyroBoschRange._2000dps)
        libmetawear.mbl_mw_gyro_bmi270_set_odr(self.device.board, GyroBoschOdr._100Hz)
        libmetawear.mbl_mw_gyro_bmi270_write_config(self.device.board)

        if ENABLE_MAG :
            libmetawear.mbl_mw_mag_bmm150_stop(self.device.board)
            libmetawear.mbl_mw_mag_bmm150_set_preset(self.device.board, MagBmm150Odr._25Hz)

        # get acc signal
        acc = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
        # get gyro signal - MMRl, MMR, MMc ONLY
        #gyro = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(self.device.board)
        # get gyro signal - MMRS ONLY
        gyro = libmetawear.mbl_mw_gyro_bmi270_get_rotation_data_signal(self.device.board)

        if ENABLE_MAG :
            mag = libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal(self.device.board)

        
        # create signals variable
        if ENABLE_MAG :
            signals = (c_void_p * 2)()
            signals[0] = gyro
            signals[1] = mag
        else :
            signals = (c_void_p * 1)()
            signals[0] = gyro

        # create acc + gyro signal fuser
        if ENABLE_MAG :
            libmetawear.mbl_mw_dataprocessor_fuser_create(acc, signals, 2, None, fn_wrapper)
        else :
            libmetawear.mbl_mw_dataprocessor_fuser_create(acc, signals, 1, None, fn_wrapper)

        # wait for fuser to be created
        e.wait()
        # subscribe to the fused signal
        libmetawear.mbl_mw_datasignal_subscribe(self.processor, None, self.callback)
    # start
    def start(self):
        # start gyro sampling - MMRL, MMC, MMR only
        #libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(self.device.board)
        # start gyro sampling - MMS ONLY
        libmetawear.mbl_mw_gyro_bmi270_enable_rotation_sampling(self.device.board)
        # start acc sampling
        libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
        # start gyro - MMRL, MMC, MMR only
        #libmetawear.mbl_mw_gyro_bmi160_start(self.device.board)
        if ENABLE_MAG :
            libmetawear.mbl_mw_mag_bmm150_enable_b_field_sampling(self.device.board)
        # start gyro sampling - MMS ONLY
        libmetawear.mbl_mw_gyro_bmi270_start(self.device.board)
        # start acc
        libmetawear.mbl_mw_acc_start(self.device.board)

        if ENABLE_MAG :
            libmetawear.mbl_mw_mag_bmm150_start(self.device.board)

    def stop(self):
        libmetawear.mbl_mw_gyro_bmi270_disable_rotation_sampling(self.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
        libmetawear.mbl_mw_mag_bmm150_disable_b_field_sampling(self.device.board)

    def reset(self):
        # stop logging
        libmetawear.mbl_mw_logging_stop(self.device.board)
        sleep(1.0)

        # flush cache if mms
        libmetawear.mbl_mw_logging_flush_page(self.device.board)
        sleep(1.0)

        # clear logger
        libmetawear.mbl_mw_logging_clear_entries(self.device.board)
        sleep(1.0)

        # remove events
        libmetawear.mbl_mw_event_remove_all(self.device.board)
        sleep(1.0)

        # erase macros
        libmetawear.mbl_mw_macro_erase_all(self.device.board)
        sleep(1.0)

        # debug and garbage collect
        libmetawear.mbl_mw_debug_reset_after_gc(self.device.board)
        sleep(1.0)

        
# connect
# E3:8A:50:5F:B1:60 DC:AD:29:8D:23:1B EE:A2:3E:AE:E2:87
for i in range(len(argv) - 1):
    d = MetaWear(argv[i + 1])

    while(True) :
        try :
            d.connect()
        except :
            print("Connected Failed, Reconnect!")
        else :
            break

    print("Connected to " + d.address + " over " + ("USB" if d.usb.is_connected else "BLE"))
    states.append(State(d))


# reset
print("Resetting devices")
for s in states:
    s.reset()


# configure
for s in states:
    print("Configuring %s" % (s.device.address))
    s.setup()

# start
for s in states:
    s.start()


class MyThread(Thread):
    global savingState, IDLabel, IMUdir
    def __init__(self, event, s):
        Thread.__init__(self)
        self.stopped = event
        self.count = 0
        self.cur_time = 0
        self.cur_packet = ""
        self.s = s

    def run(self):
        while not self.stopped.wait(0.02):
            if len(states[0].packets) != 0 and len(states[1].packets) != 0:
                self.cur_packet = str(int(round(time.time() * 1000))) + " " + states[0].packets.pop() + " " + states[1].packets.pop()
                #self.s.send(thread.cur_packet.encode())
                #print(int(round(time.time() * 1000))-self.cur_time, self.cur_packet, self.count)
                self.cur_time = int(round(time.time() * 1000))
                self.count += 1
                if savingState == True and IDLabel != "stopRecording":
                    fileName = IMUdir + IDLabel + ".json"
                    with open(fileName, 'a') as f:
                        json.dump(thread.cur_packet, f)
                        f.close()
                
    
def recvData():
    global savingState
    global IDLabel
    global IMUdir, IMGdir
    while True:
        IDLabel = s.recv(1024).decode()
        if(IDLabel != 0):
            print(IDLabel)
            if str(IDLabel) != "stopRecording":
                savingState = True
                dir = IDLabel.split("_")
                if len(dir) == 3:
                    IMUdir = "./Data/IMU/"+dir[1]+"/"+dir[0]+"/"
                    IMGdir = "./Data/IMG/"+dir[1]+"/"+dir[0]+"/"+dir[2]+"/"
                    if os.path.exists(IMUdir) != True:
                        os.makedirs(IMUdir, mode=0o777)
                    if os.path.exists(IMGdir) != True:
                        os.makedirs(IMGdir, mode=0o777)

            else :
                savingState = False

def captureIMG():
    global savingState, IMGdir, IDLabel
    capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if capture.isOpened() :
        while not Event().wait(0.03):
            success, img = capture.read()
            if success:
                if savingState == True:
                    count += 1
                    cv2.imwrite(IMGdir + IDLabel +"_"+ str(count) +".jpg", img)
                else:
                    count = 0
    else:
        print("Can't Open Webcam")


# create socket
HOST = '127.0.0.1'
PORT = 5050
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


# wait 10 s
stopFlag = Event()
thread = MyThread(stopFlag, s)
thread.start()
s_thread = threading.Thread(target=recvData)
s_thread.start()
ImgFlag = Event()
img_thread = threading.Thread(target=captureIMG)
img_thread.start()

#sleep(10.0)


#stopFlag.set()
# s.close()
#
# # stop
# print("Stopping devices")
# for s in states:
#     s.stop()
#
# # reset
# print("Resetting devices")
# for s in states:
#     s.reset()
#     libmetawear.mbl_mw_debug_disconnect(s.device.board)


    
