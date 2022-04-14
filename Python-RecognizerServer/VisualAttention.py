from glob import glob
from tempfile import tempdir
from time import time

from tools.quaternion import Quaternion
import numpy as np
import math
import sys
import cv2
import matplotlib.pyplot as plt
import tqdm
import os
import time
import glob

import Configs

class RecordedData:
    def __init__(self, path):
        self.file_path = path
        self.time_tick = []
        self.total_second = [] #
        self.time_stamp = []
        self.frame_sequence = []#
        self.dir = []
        self.camera_pose = []
        self.gaze_dir = []
        self.left_openness = []
        self.right_openness = []
        self.unity_erp_dir = []
    
    def parse_data(self):
        with open(self.file_path) as f:
            lines = f.readlines()
            for line in lines:
                self.time_tick.append(int(line.split(',')[0]))
                self.total_second.append(float(line.split(',')[1]))
                self.time_stamp.append(int(line.split(',')[2]))
                self.frame_sequence.append(int(line.split(',')[3]))
                self.dir.append((
                    float(line.split(',')[4][1:]),
                    float(line.split(',')[5]),
                    float(line.split(',')[6][:-2])
                ))
                if len(line.split(',')) > 7:
                    self.camera_pose.append(
                        Quaternion.from_value(np.array([
                            float(line.split(',')[7][1:]),
                            float(line.split(',')[8]),
                            float(line.split(',')[9]),
                            float(line.split(',')[10][:-2])
                    ])))

                    self.gaze_dir.append((
                        float(line.split(',')[11][1:]),
                        float(line.split(',')[12]),
                        float(line.split(',')[13][:-2])
                    ))
                    self.left_openness.append(float(line.split(',')[14]))
                    self.right_openness.append(float(line.split(',')[15]))
                    self.unity_erp_dir.append((
                        float(line.split(',')[16][1:]),
                        float(line.split(',')[17][:-2])
                    ))

def dir_to_degree(x, y, z):
    _x = []
    _y = []
    for i in range(len(x)):
        thetaDeg = math.atan(z[i]/ (x[i] + sys.float_info.epsilon)) * 180.0 / math.pi
        #print("{}:{}, {}".format(i, x[i], z[i]))
        if (x[i] < 0.0) & (z[i] < 0.0):  # 中線左邊
            thetaDeg = 90.0 - thetaDeg
        elif (x[i] < 0.0) & (z[i] > 0.0):
            thetaDeg = 90.0 - thetaDeg
        elif (x[i] > 0.0) & (z[i] > 0.0):   # 中線右邊
            thetaDeg = 180.0 + (90.0 - thetaDeg)
        else:
            thetaDeg = 270.0 + (- thetaDeg)

        thetaDeg2 = 0.0
        if thetaDeg - 90.0 < 0.0:
            thetaDeg2 = (thetaDeg - 90.0) + 360.0
        else:
            thetaDeg2 = (thetaDeg - 90.0)
        
        phiDeg = math.acos(y[i]) * 180 / math.pi

        _x.append(thetaDeg)
        _y.append(phiDeg)
    return _x, _y

def read_raw_data_file(file_path):
    record = RecordedData(file_path)
    record.parse_data()
    x = [d[0] for d in record.dir]
    y = [d[1] for d in record.dir]
    z = [d[2] for d in record.dir]
    
    _x, _y = dir_to_degree(x, y, z)
    
    return record.total_second, record.frame_sequence, _x, _y, x, y, z

def sqrtCheck(x):
    if x < 0:
        return 0.5
    else:
        return math.sqrt(x)

def fixation_detection(x, y, time, seq, missing=0.0, maxdist=0.0, mindur=80):
    """ Find fixations from raw gaze date (based on distance and duration)
        maxdist=0.08 (80 degree/1000 micro-second)
	    mindur=80 (80 millisecond)

        Parameters
        ----------
        
        Returns
        ----------
    # fixation_list[1]: [startime, endtime, seq.start, seq.end, duration, end_x, end_y]    
    """
    # empty list to contain data 
    Sfix = [] # [starttime]
    Efix = [] # [starttime, endtime, duration, end_x, end_y]

	# loop through all coordinates
    si = 0
    fixstart = False
    for i in range(1, len(x)):
        # calculate Euclidean distance from the current fixation coordinate
        # to the next coordinate
        
        #dist = math.acos(
        #    (math.sin(y[i])*math.sin(y[si]) + math.cos(y[i])*math.cos(y[si])*math.cos(x[i] - x[si]))
        #)
        delta_lan = math.radians(y[si] - y[i])
        delta_lon = math.radians(x[si] - x[i])
        dist = 2 * math.asin(
            min(
                math.sqrt(
                    sqrtCheck(math.sin(delta_lan/2)*math.sin(delta_lan/2) + math.cos(y[si])*math.cos(y[i])*math.sin(delta_lon/2)*math.sin(delta_lon/2))
                ),
                1.0
            )
        )
        dist = math.degrees(dist)
        #print(dist)
        # check if the next coordinate is below maximal distance
        if dist <= maxdist and not fixstart:
            # start a new fixation
            si = 0 + i
            fixstart = True
            Sfix.append([time[i], seq[i]])
        elif dist > maxdist and fixstart:
            
            # end the current fixation
            fixstart = False
            # only store the fixation if the duration is ok
            dur = (time[i-1]-Sfix[-1][0])*1000
            #print(dur)
            if  dur >= mindur:
                Efix.append([Sfix[-1][0], time[i-1], Sfix[-1][1], seq[i-1], time[i-1]-Sfix[-1][0], x[si], y[si]])
            # delete the last fixation start if it was too short
            else:
                Sfix.pop(-1)
            si = 0 + i
        elif not fixstart:
            si += 1
    return Sfix, Efix

def get_gaze_data(data_path, direct_list, gaze_list, raw):
    time, sequence, _x, _y, x, y, z= read_raw_data_file(data_path)

    fixation_list = fixation_detection( x=_x, 
                                        y=_y, 
                                        time=(np.asarray(time) - time[0]), 
                                        seq=(np.asarray(sequence) - sequence[0]),
                                        maxdist=80,
                                        mindur=80)[1]

    f_time = [ [fixation[0], fixation[1]] for fixation in fixation_list]

    if raw:
        for i in range(0, len(time)):
            # eye direaction in three-dimension
            direct_list.append([[],[],[]])
            direct_list[i][0].append(x[i])
            direct_list[i][1].append(y[i])
            direct_list[i][2].append(z[i])

            # gaze coordinate in two-dimension
            gaze_list.append([[],[]])
            gaze_list[i][0].append(int(_x[i]))
            gaze_list[i][1].append(int(_y[i]))

def py_make_gauss_mask(x, y, sigma=2):
    fixTime = np.ones(len(x))
    w = 1
    w = w*30

    my_sigma = sigma #w/(2*math.sqrt(2*math.log(2)))
    r = 180
    c = 360

    big_r = 2*r + 1
    big_c = 2*c + 1

    d1, d2 = np.meshgrid(np.arange(big_c), np.arange(big_r))
    my_mask = np.zeros((r, c))
    
    temp_num = (d1-c)**2 + (d2-r)**2
    temp = np.exp(-temp_num/(2*my_sigma**2))
    big_gauss = temp/(2*np.pi*my_sigma)


    for i in range(len(x)):
        temp_x = math.floor(np.clip(x[i], 0, c))
        temp_y = math.floor(np.clip(y[i], 0, r))
        temp = big_gauss[r-temp_y:r-temp_y+r, c-temp_x:c-temp_x+c]
        my_mask = my_mask + temp*fixTime[i]

    my_mask = my_mask/np.amax(my_mask)
    
    return my_mask

def export_debug_video(path_root, serial, train_id, round_id, num_of_samples, gt_frames, direct_list):
    cm = plt.get_cmap('jet_r')
    
    output_fps = 2 if num_of_samples == 30 else 30
    output_path = '{}/{}/{}.avi'.format(path_root, train_id, round_id)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), output_fps, (Configs.ATTENTION_VIDEO_SIZE))
    print(' - Export debug video...  , Round : ' + str(round_id))
    pbar = tqdm.tqdm(total=num_of_samples)
    for f in range(1, num_of_samples+1):
        pbar.update(1)
        colored_frame = cv2.resize(cm(gt_frames[f-1]), Configs.ATTENTION_VIDEO_SIZE, interpolation=cv2.INTER_AREA)
        colored_arr = (colored_frame[:, :, 0:3]*255).astype(np.uint8)   # attention

        STIMULUS_FRAME_PATH = 'Dataset/{}/{}/Panorama{}.jpg'.format(serial, train_id, round_id)
        
        stimulus_frame = cv2.resize(cv2.imread(STIMULUS_FRAME_PATH), Configs.ATTENTION_VIDEO_SIZE, interpolation=cv2.INTER_AREA)
        debug_frame = cv2.addWeighted(stimulus_frame, 0.4, colored_arr, 0.6, 0.0)

        cv2.rectangle(debug_frame, (0, 0), (350, 80), (255, 255, 255), -1)
        dirText = "(" + str(direct_list[f-1][0]) + ", " + str(direct_list[f-1][1]) + ", " + str(direct_list[f-1][2]) + ")"
        cv2.putText(debug_frame, dirText, (0,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 1, cv2.LINE_AA)
        out.write(debug_frame)

    pbar.close()
    out.release()

def export_ground_truth_sequence(path_root, serial, train_id, round_id, direct_list, gaze_list, sigma, debug):
    gt_frames = []

    print(" - Convert gaze to mask... , Round : " + str(round_id))

    pbar = tqdm.tqdm(total=len(gaze_list))
    for f in range(1, len(gaze_list)+1):
        pbar.update(1)
        conv_image = py_make_gauss_mask(gaze_list[f-1][0], gaze_list[f-1][1], sigma=sigma)
        result_image = cv2.resize(conv_image, (Configs.ATTENTION_WIDTH, Configs.ATTENTION_HEIGHT), interpolation=cv2.INTER_LINEAR)
        if debug:
            small_frame = cv2.resize(conv_image, Configs.ATTENTION_VIDEO_SIZE, interpolation=cv2.INTER_AREA)
            gt_frames.append(small_frame)
    pbar.close()

    if debug:
        export_debug_video(path_root, serial, train_id, round_id, len(gaze_list), gt_frames, direct_list)

def generate_ground_truth(debug, sigma):
    for TRAIN_ID in range(1, Configs.train_num + 1):
        for ROUND_ID in range(0, Configs.round_num):
            direct_list = []
            gaze_list = []

            target_gazefile_path = 'Dataset/{}/{}/{}.txt'.format(Configs.user_serial_id, TRAIN_ID, ROUND_ID)
            raw_gazefile_path = glob.glob(target_gazefile_path)[0]
            get_gaze_data(raw_gazefile_path, direct_list, gaze_list, raw=True)
            export_ground_truth_sequence(os.path.abspath('Visualization/' + str(Configs.user_serial_id)), Configs.user_serial_id, TRAIN_ID, ROUND_ID, direct_list, gaze_list, sigma, debug)

def attention_main():
    time_start = time.time()
    generate_ground_truth(True, 5)
    time_end = time.time()
    print('Execution time: {} s'.format((time_end-time_start)))

