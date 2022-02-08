from pathlib import Path
import math
import numpy as np
import os
import cv2

# For PyQt5
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *

# For PyQtgraph
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

# For PyQt5 Connect To YOLO
from yolov4 import *

# For YOLO
# from tool.utils import *
# from tool.torch_utils import *
# from tool.darknet2pytorch import Darknet
# from tool.draw_trajectory import *

# For OpenPose
from openpose import *

top, left, width, height = 0, 0, 1280, 720

    
class OpenPose():
    def __init__(self):
        super(OpenPose, self).__init__()

    def pose_detect(self, img):
        img, value = openpose_detect(img)

        return img, value

    def pose_detect_with_revise(self, img, lastpose):
        img, value = openpose_detect(img)
        value = self.revise_value(value, lastpose)

        return img, value

    def revise_value(self, pose, lastpose):
        
        # 檢查 value 裡面有沒有 detect 為 0 的。若有就補上前面幾個 frame 的資訊
        for i in range(0, 25):
            keyx, keyy = pose[0][i][0], pose[0][i][1]

            if((keyx == 0 and keyy == 0)):
                pose[0][i][0] = lastpose[0][i][0]
                pose[0][i][1] = lastpose[0][i][1]
        
        return pose

class YOLOv4():
    def __init__(self):
        super(YOLOv4, self).__init__()
        # 載入必要 cfg、weights、class_names 檔案
        self.model = Darknet("cfg/yolov4-obj.cfg")
        self.model.load_weights("weights/yolov4_finetune.weights")
        self.class_names = load_class_names('data/x.names')

        if use_cuda:
            self.model.cuda()
    
    # 回傳 y-value 和 bbox 
    def ball_detect(self, img):
        yvalue, bbox = detect_cv2(self.model, img, self.class_names)
        return yvalue, bbox

    def plot_boxes(self, img, boxes):
        img = plot_boxes_cv2(img, boxes[0], savename=None, class_names=self.class_names)
        return img

    def plot_ballcenter(self, img, boxes):
        p1x, p1y = boxes[0][0][0]*1280, boxes[0][0][1]*720
        p2x, p2y = boxes[0][0][2]*1280, boxes[0][0][3]*720
        bcx, bcy = (p1x + p2x)/2, (p1y + p2y)/2

        point_size = 5
        point_color = (255, 255, 255)
        thickness = -1

        cv2.circle(img, (int(bcx), int(bcy)), point_size, point_color, thickness)
        return img


YOLOv4 = YOLOv4()
OpenPose = OpenPose()

# 運球的種類、Loop 判斷
class DribbleVideo():
    def __init__(self):
        super(DribbleVideo, self).__init__()

        self.path = ""
        self.filename = ""
        self.state = -1
        self.frame_id = 0
        self.dribble_type = "None"
        self.wave_type = "None"
        self.wave_count = 0
        self.startcut = False
        self.endcut = False
        self.substart = -1
        self.subend = -1
        self.down_list = []            # 存放波峰 frame id
        self.up_list = []

        self.frameimg_list = []      # 存放讀入的影片所有 frame 截圖
        self.visualimg_list = []
        self.resultimg_list = []
        self.saveclip_info = []          # 存放所有可以儲存的片段資訊
        self.posecoor_list = []
        self.ballcoor_list = []

    # 初始化丟入的影片資訊
    def Init_VideoInfo(self, path):
        self.path = path
        self.filename = ""
        self.state = -1
        self.frame_id = 0
        self.dribble_type = "None"
        self.wave_count = "None"
        self.wave_count = 0
        self.startcut = False
        self.endcut = False
        self.substart = -1
        self.subend = -1
        self.down_list = []            # 存放波峰 frame id
        self.up_list = []

        self.frameimg_list = []      # 存放讀入的影片所有 frame 截圖
        self.visualimg_list = []
        self.resultimg_list = []
        self.saveclip_info = []          # 存放所有可以儲存的片段資訊
        self.posecoor_list = []
        self.ballcoor_list = []

        # E:\System\OpenPose\build\examples\tutorial_api_python
        _path = Path(path)
        _parentpath = _path.parent.absolute()
        basename = str(os.path.basename(os.path.normpath(path)))
        # self.filename = self.path.replace(str(_parentpath), "")
        # self.filename = basename
        self.filename = self.path
        print("=====")
        print(self.filename)
        print("=====")
        # self.Detect_DribbleType(self.filename)    # 檢查現在丟入的影片是哪種運球種類
        self.Detect_DribbleType(self.path)

    # 依據傳入的 filenmae，判斷此影片的 Dribble Type
    def Detect_DribbleType(self, filename):
        if "SH" in filename:
            self.dribble_type = "S"
        elif "CO" in filename:
            self.dribble_type = "D"
        elif "BH" in filename:
            self.dribble_type = "D"
        elif "BL" in filename:
            self.dribble_type = "D"
        elif "LP" in filename:
            self.dribble_type = "S"

    # 依據輸入 frame id，判斷現在是否有發生 wave，以及是哪一種 wave
    def Detect_DribbleWave(self, plot_info):
        wave_type = "None"
        if(self.frame_id < 2):
            pass
        else:
            p1_y = plot_info[self.frame_id]   # 最新
            p2_y = plot_info[self.frame_id-1] # 舊
            p3_y = plot_info[self.frame_id-2] # 最舊

            # 如果 v1 v2 是 + 代表往下走，如果 v1 v2 是 - 代表下上走
            v1 = p1_y - p2_y # 新
            v2 = p2_y - p3_y # 舊

            # 如果 兩個 異號 代表達波峰或波谷
            if(v1 * v2 < 0):
                self.wave_count = self.wave_count + 1
                if(v1 > 0 and v2 < 0): # v1 向上走 波谷
                    wave_type = "up"
                    self.up_list.append(self.frame_id - 1)
                if(v1 < 0 and v2 > 0):
                    wave_type = "down"
                    self.down_list.append(self.frame_id - 1)

        return wave_type


class CutToClip():
    def __init__(self):
        super(CutToClip, self).__init__()

        self.start_frame = -1
        self.end_frame = -1
        self.root = ""          # 用來設定儲存根路徑
        self.filenmae = ""      # 用來設定儲存檔案
        self.colors = [ #BGR
            (51, 0, 153), 
            (0, 0, 214), 
            (0, 71, 214), 
            (0, 143, 214), 
            (0, 214, 214),
            (0, 214, 143), 
            (0, 214, 71), 
            (0, 153, 0), 
            (0, 0, 153), 
            (21, 153, 0), 
            (102, 153, 0), 
            (153, 153, 0),
            (153, 102, 0),
            (153, 51, 0),
            (153, 0, 0),
            (102, 0, 153),
            (153, 0, 102),
            (153, 0, 153),
            (153, 0, 51),
            (153, 0, 0),
            (153, 0, 0),
            (153, 0, 0),
            (153, 153, 0),
            (153, 153, 0),
            (153, 153, 0)
        ]

        self.boneconnect = [
            [17, 15], [15, 0], [0, 16], [16, 18], [0, 1], [1, 2],
            [2, 3],
            [3, 4],
            [1, 5],
            [5, 6],
            [6, 7],
            [1, 8],
            [8, 9],
            [9, 10],
            [10, 11],
            [11, 24],
            [11, 22],
            [22, 23],
            [8, 12],
            [12, 13],
            [13, 14],
            [14, 21],
            [14, 19],
            [19, 20]
        ]

        self.bonecolor = [
            (153, 0, 153),
            (102, 0, 153),
            (153, 0, 102),
            (153, 0, 51),
            (51, 0, 153),
            (0, 51, 153),
            (0, 102, 153),
            (0, 153, 153),
            (0, 153, 102),
            (0, 153, 51),
            (0, 153, 0),
            (0, 0, 153),
            (51, 153, 0),
            (102, 153, 0),
            (153, 153, 0),
            (153, 153, 0),
            (153, 153, 0),
            (153, 153, 0),
            (153, 102, 0),
            (153, 51, 0),
            (153, 0, 0),
            (153, 0, 0),
            (153, 0, 0),
            (153, 0, 0)
        ]

    
    def SetUp_Clip(self, sf, ef, root):
        self.start_frame = sf
        self.end_frame = ef
        self.root = root
        self.filename = root + "_sf" + str(sf) + "_ef" + str(ef) + ".mp4"

    def Save_Clip(self, imglist, visualimglist, posecoor_list, ballcoor_list):
        print(self.filename)
        path = "dribbling-video/Total Clip/" + self.filename.replace("dribbling-video/", "")
        print(path)
        path = self.filename.replace("dribbling-video/", "")
        print(path)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        clip = cv2.VideoWriter(path, fourcc , 20.0, (1280, 720))


        # blank_img = np.zeros((height, width, 3), np.uint8)


        for i in range(self.start_frame, self.end_frame):
            clip.write(imglist[i])
            # blank_img = self.Draw_Pose(blank_img, posecoor_list[i], i)
            # blank_img = self.Draw_Ball(blank_img, ballcoor_list[i])
            # cv2.waitKey(0)

        # imgname = "Cut/" + self.filename.replace("Normalize/", "").replace(".mp4", "") + ".jpg"
        # cv2.imwrite(imgname, blank_img)


    def Save_Draw(self, posecoor_list, ballcoor_list, totalf):
        
        for i in range(totalf):
            imgname = "dribbling-video/pose_and_ball/" + str(i) + ".jpg" # 設定純放路徑
            blank_img = np.zeros((height, width, 3), np.uint8)  # 創建底圖
            blank_img = self.Draw_Pose(blank_img, posecoor_list, i)
            blank_img = self.Draw_Ball(blank_img, ballcoor_list, i)

            cv2.imwrite(imgname, blank_img)





    def Draw_Pose(self, img, posecoor_list, frame_id):
        # Bone 骨架
        pose = posecoor_list[frame_id]
        for i in range(0, 24):
            cp1, cp2 = self.boneconnect[i][0], self.boneconnect[i][1]   # cp1、cp2 為要畫連線的點
            point_color = self.bonecolor[i]
            key1x, key1y = pose[0][cp1][0], pose[0][cp1][1]
            key2x, key2y = pose[0][cp2][0], pose[0][cp2][1]
            if((key1x == 0 and key1y == 0) or (key2x == 0 and key2y == 0)):
                continue
            cv2.line(img, (key1x, key1y), (key2x, key2y), point_color, 3)

        # Joint 關節
        for i in range(0, 25):
            keyx, keyy = pose[0][i][0], pose[0][i][1]

            point_size = 7
            point_color = self.colors[i]
            thickness = -1

            if((keyx == 0 and keyy == 0)):
                continue
            cv2.circle(img, (int(keyx), int(keyy)), point_size, point_color, thickness)

        return img

    def Draw_Ball(self, img, ballcoor_list, frame_id):
        
        ball = ballcoor_list[frame_id]
        bcx, bcy = ball[0], ball[1]

        point_size = 3
        point_color = (255, 255, 255)
        thickness = -1

        cv2.circle(img, (int(bcx), int(bcy)), point_size, point_color, thickness)

        return img


class Ui_MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)

        # self.OpenPose = OpenPose()
        # self.YOLOv4 = YOLOv4()
        self.Video = DribbleVideo()

        self.timer_camera = QtCore.QTimer()  # 初始化定时器
        self.cap = cv2.VideoCapture(0)  # 初始化摄像头

        self.Video.frame_id = 0
        self.wave_count = 0
        self.dribble_type = ""  # 紀錄先在丟入的影片是哪種運球種類
        self.plot_info = []

        self.UI_init()
        self.slot_init()

    def UI_init(self):

        self.setWindowTitle(u'Dribbling Clip')
        self.setGeometry(top, left, width, height)
        self.setStyleSheet("background-color: black;")

        self.__layout_main = QtWidgets.QVBoxLayout()  
        self.__layout_function = QtWidgets.QHBoxLayout()
        self.__layout_data_show = QtWidgets.QVBoxLayout()
        self.__layout_video_detail = QtWidgets.QHBoxLayout()

        # 上面區段：(功能)開啟影片
        self.text_filepath = QLineEdit() 
        self.button_openfile = QPushButton(u'Open File')
        self.button_saveclip = QPushButton(u'Save Clip')
        buttons = [self.button_openfile, self.button_saveclip]
        self.Ui_Function_Setting(buttons)

        # 中間區段：(顯示)Camera + Console
        self.Camera_Screen = QLabel()
        self.Ui_CameraScreen_Clear()
        self.Video_Slider = QSlider(Qt.Horizontal)
        self.Ui_VideoSlider_Setup()
        self.Detail_Console = QTextEdit()
        self.Ui_DetailConsole_Clear()
        

        # 下面區段：(顯示)籃球y軸折線圖
        self.Plot_Canvas = pg.PlotWidget()
        # self.Plot_Canvas = Ui_PlotCanvas()  
        self.Ui_PlotCanvas_Clear()
        self.timeline = pg.InfiniteLine(angle = 90, movable = True, label='frame = {value:0.1f}', pen = 'r', hoverPen = 'w', labelOpts={'position':0.1, 'color':(255, 255, 255), 'fill':(255, 0, 0, 50)} )
        self.yvalueline = pg.InfiniteLine(angle = 0, movable = False, label='yvalue = {value:0.2f}', pen = 'y', labelOpts={'position':0.1, 'color':(255, 255, 255), 'fill':(255, 255, 0, 50)})
        self.Plot_Canvas.addItem(self.timeline)
        self.Plot_Canvas.addItem(self.yvalueline)
        self.curve = self.Plot_Canvas.plot()
        self.Ui_PlotCurve_Clear()


        # 將物件們組裝成視窗畫面
        self.__layout_function.addWidget(self.text_filepath)
        self.__layout_function.addWidget(self.button_openfile)
        self.__layout_function.addWidget(self.button_saveclip)

        self.__layout_video_detail.addWidget(self.Camera_Screen, alignment = Qt.AlignCenter)
        self.__layout_video_detail.addWidget(self.Detail_Console)

        self.__layout_data_show.addLayout(self.__layout_video_detail)
        # self.__layout_data_show.addWidget(self.Video_Slider)
        self.__layout_data_show.addWidget(self.Plot_Canvas)

        self.__layout_main.addLayout(self.__layout_function)
        self.__layout_main.addLayout(self.__layout_data_show)

        self.setLayout(self.__layout_main)

    def Ui_Function_Setting(self, buttons):
        # Button
        for i in range(2):
            buttons[i].setStyleSheet(
                "QPushButton{color:black}"
                "QPushButton:hover{color:black}"
                "QPushButton{background-color:rgb(255,255,255)}"
                "QPushButton:hover{background-color:rgb(200, 200, 200)}"
            )
        self.button_openfile.setEnabled(True)


        # LineText
        self.text_filepath.setStyleSheet(
            "QLineEdit{background-color:rgb(255, 255, 255)}"
        )
        self.text_filepath.setReadOnly(True)

    def Ui_CameraScreen_Clear(self):
        self.Camera_Screen.setFixedSize(640, 360)
        self.Camera_Screen.setText("Dribbling Video")
        self.Camera_Screen.setStyleSheet(
            "color: rgb(255,255,255);"
            "font:20px 'Times New Roman';"
            "border: 1px solid white;"
        )

    def Ui_VideoSlider_Setup(self):
        self.Video_Slider.setRange(0,0)
        self.Video_Slider.sliderMoved.connect(self.Ui_VideoSlider_Set)
    
    # 拉動 Slider 軸的時候
    def Ui_VideoSlider_Set(self, position):
        # print(position)
        self.timeline.setPos(position)
        self.yvalueline.setPos(self.plot_info[position])
        frame = self.Video.resultimg_list[position]
        frame = cv2.resize(frame, (640, 360))
        frameImage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        self.Camera_Screen.setPixmap(QtGui.QPixmap.fromImage(frameImage))

    def Ui_VideoSlider_Clear(self):
        self.Video_Slider.setValue(0)

    # 在分析完之後，更改 Slider 的 Range 範圍
    def Ui_VideoSlider_Change(self, duration):
        self.Video_Slider.setRange(0, duration)

    def Ui_DetailConsole_Clear(self):
        self.Detail_Console.clear()
        self.Detail_Console.setReadOnly(True)
        self.Detail_Console.setStyleSheet(
            "color:rgb(255,255,255);"
            "font:20px 'Times New Roman';"
        )
    
    def Ui_PlotCanvas_Clear(self):
        self.Plot_Canvas.showGrid(x=False, y = False)
        self.Plot_Canvas.setLabels(
            bottom = ' Time (frame) ',
            left = 'Ball Y Value (coordinate in window)'
        )

    # def Ui_PlotCanvas_Set(self):
        # self.Plot_Canvas.setLimits(xMin = -0.5, xMax = self.Video.frame_id - 1+0.5, yMin = -720 , yMax = 0)
    
    def Ui_PlotCurve_Clear(self):
        self.plot_info.clear()
        self.curve.setData(self.plot_info)




    # 物件與 handler 連結
    def slot_init(self):
        self.timer_camera.timeout.connect(self.show_camera)
        self.button_openfile.clicked.connect(self.open_file)
        self.button_saveclip.clicked.connect(self.save_clip)
        self.timeline.sigDragged.connect(self.timeline_sigDragged)

    # 開啟檔案
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Video")
        # 成功載入
        if path != '':
            # 如果成功讀取檔案，初始化影片資訊
            self.Video.Init_VideoInfo(path)
            self.text_filepath.setText(self.Video.path)         # 更新 (上半部 功能處) 顯示路徑
            self.cap = cv2.VideoCapture(self.Video.filename)    # 更新 (中間段 影片顯示處) 讀取來源
            self.Ui_DetailConsole_Clear()                       # 清空 (中間段 細節顯示處) 所有細節
            self.Ui_PlotCurve_Clear()                           # 清空 (下半部 繪圖區) 折線與索取資料
            self.Ui_VideoSlider_Clear()
            self.timeline.setPos(0)
            self.yvalueline.setPos(0)
            self.timer_camera.start(30)

    # 儲存所有 clip
    def save_clip(self):
        
        # 針對未切影片
        # 單手
        # if(self.Video.dribble_type == "S"):
        #     for i in range(len(self.Video.down_list) - 1):
        #         print(str(self.Video.down_list[i]) + "是波峰")
        #         objClip = CutToClip()
        #         objClip.SetUp_Clip(self.Video.down_list[i], self.Video.down_list[i+1], self.Video.filename.replace(".mp4", ""))
        #         self.Video.saveclip_info.append(objClip)
        # # 雙手
        # elif(self.Video.dribble_type == "D"):
        #     for i in range(len(self.Video.down_list) - 2):
        #         print(str(self.Video.down_list[i]) + "是波峰")
        #         objClip = CutToClip()
        #         objClip.SetUp_Clip(self.Video.down_list[i], self.Video.down_list[i+2], self.Video.filename.replace(".mp4", ""))
        #         self.Video.saveclip_info.append(objClip)


        # 單手
        # if(self.Video.dribble_type == "S"):
        # for i in range(len(self.Video.down_list) - 1):
        #     print(str(self.Video.down_list[i]) + "是波峰")
        #     objClip = CutToClip()
        #     objClip.SetUp_Clip(self.Video.down_list[i], self.Video.down_list[i+1], self.Video.filename.replace(".mp4", ""))
        #     self.Video.saveclip_info.append(objClip)
        # # 雙手
        # elif(self.Video.dribble_type == "D"):
        for i in range(len(self.Video.down_list) - 2):
            print(str(self.Video.down_list[i]) + "是波峰")
            objClip = CutToClip()
            objClip.SetUp_Clip(self.Video.down_list[i], self.Video.down_list[i+2], self.Video.filename.replace(".mp4", ""))
            self.Video.saveclip_info.append(objClip)

        # 針對切過的影片

        # objClip = CutToClip()
        # objClip.SetUp_Clip(0, self.Video.frame_id-1, self.Video.filename.replace(".mp4", ""))
        # self.Video.saveclip_info.append(objClip)

        # 從 self.Video.frameimg_list 裡面抓圖片出來儲存
        for i in range(len(self.Video.saveclip_info)):
            # if(i == 0):
            #     self.Video.saveclip_info[i].Save_Draw(self.Video.posecoor_list, self.Video.ballcoor_list, self.Video.frame_id-1)
            self.Video.saveclip_info[i].Save_Clip(self.Video.frameimg_list, self.Video.visualimg_list, self.Video.posecoor_list, self.Video.ballcoor_list)




        # 把每一個 frame 的 pose and ball 畫成 image




    # 在 DetailConsole 處列出第幾 frame 是波峰 or 波谷
    def Ui_DetailConsole_List(self):
        self.Detail_Console.append("波峰發生位置 : ")
        for i in range(len(self.Video.down_list)):
            self.Detail_Console.append("frame " + str(self.Video.down_list[i]))


    def show_camera(self):
        flag, self.image = self.cap.read()
        if(flag != True):
            # 影片讀取結束後 只需要呼叫一次的
            if(self.Video.video_state == 0):
                self.button_openfile.setEnabled(True)   # 開啟檔案按鈕可使用設置
                # self.Ui_PlotCanvas_Set()        # 設置畫布
                self.Ui_DetailConsole_List()    # 列出波峰位置
                self.Ui_VideoSlider_Change(self.Video.frame_id-1)   # Slider 設置
                # self.Ui_PlotCurve_Update()  # 畫曲線圖
                self.Video.video_state = -1

            # self.cap.release()
        else:
            # self.image = cv2.flip(self.image, 0)
            # self.image = cv2.flip(self.image, 1)
            self.Video.video_state = 0
            self.button_openfile.setEnabled(False)

            self.Video.frameimg_list.append(self.image)
            if(self.Video.frame_id == 0):
                frame, pose = OpenPose.pose_detect(self.image)
            elif(self.Video.frame_id != 0):
                frame, pose = OpenPose.pose_detect_with_revise(self.image, self.Video.posecoor_list[self.Video.frame_id-1])
            
            plot_value, bbox = YOLOv4.ball_detect(self.image)
            
            p1x, p1y = bbox[0][0][0]*1280, bbox[0][0][1]*720
            p2x, p2y = bbox[0][0][2]*1280, bbox[0][0][3]*720
            bcx, bcy = (p1x + p2x)/2, (p1y + p2y)/2

            self.Video.posecoor_list.append(pose)
            self.Video.ballcoor_list.append([int(bcx), int(bcy)])


            # frame = YOLOv4.plot_boxes(frame, bbox)
            frame = YOLOv4.plot_ballcenter(frame, bbox)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.Video.visualimg_list.append(frame)



            self.Video.resultimg_list.append(frame)
           
            frame = cv2.resize(frame, (640, 360))
            
            frameImage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            self.Camera_Screen.setPixmap(QtGui.QPixmap.fromImage(frameImage))

            self.plot_info.append(-plot_value)
            wave_type = self.Video.Detect_DribbleWave(self.plot_info)
            self.Ui_VideoSlider_Change(self.Video.frame_id-1)   # Slider 設置
            self.Ui_PlotCurve_Update()  # 畫曲線圖

            print(self.timeline.getPos()[0])
            
            self.Video.frame_id = self.Video.frame_id + 1

    def Ui_PlotCurve_Update(self):  
        self.curve.setData(self.plot_info)
        self.timeline.setPos(self.Video.frame_id)
        self.yvalueline.setPos(self.plot_info[self.Video.frame_id])

    def timeline_sigDragged(self):
        # 取得現在位置
        currentPos = self.timeline.getPos()[0]

        if(currentPos < 0):
            nextPose = 0
        elif(currentPos > self.Video.frame_id-1):
            nextPose = self.Video.frame_id-1
        else:
            if(currentPos > int(currentPos)):
                nextPose = int(currentPos) + 1
            elif(currentPos < int(currentPos)):
                nextPose = int(currentPos) - 1

        self.timeline.setPos(nextPose)
        self.yvalueline.setPos(self.plot_info[nextPose])

        frame = self.Video.resultimg_list[nextPose]
        frame = cv2.resize(frame, (640, 360))
        frameImage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        self.Camera_Screen.setPixmap(QtGui.QPixmap.fromImage(frameImage))

        
        


if __name__ == '__main__':
    App = QApplication(sys.argv)
    win = Ui_MainWindow()
    win.show()
    sys.exit(App.exec_())
