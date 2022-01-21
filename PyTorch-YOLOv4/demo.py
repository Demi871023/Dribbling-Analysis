from tool.utils import *
from tool.torch_utils import *
from tool.darknet2pytorch import Darknet
import argparse
from tool.draw_trajectory import *

"""hyper parameters"""
use_cuda = True

def detect_cv2(cfgfile, weightfile, imgfile):
    import cv2
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if use_cuda:
        m.cuda()

    num_classes = m.num_classes
    if num_classes == 20:
        namesfile = 'data/voc.names'
    elif num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/x.names'
    class_names = load_class_names(namesfile)

    img = cv2.imread(imgfile)
    sized = cv2.resize(img, (m.width, m.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.6, use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    plot_boxes_cv2(img, boxes[0], savename='predictions.jpg', class_names=class_names)
    print(boxes[0])

def detect_cv2_video(cfgfile, weightfile, videofile):
    import cv2
    import math
    import numpy as np
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if use_cuda:
        m.cuda()

    cap = cv2.VideoCapture(videofile)
    cap.set(3, 1280)
    cap.set(4, 720)
    print("Starting the YOLO loop...")

    num_classes = m.num_classes
    if num_classes == 20:
        namesfile = 'data/voc.names'
    elif num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/x.names'
    class_names = load_class_names(namesfile)


    # Demi_Edit_Start
    from pathlib import Path

    # => create folder for result image, video and txt file
        # result_path : 創建目前 case 根目錄資料夾
        # result_txt : result_path + "/bbox.txt"
        # result_video : result_path + "/output.mp4"
        # result_img : result_path + "save_id.jpg"

        # frame id
    id = 1

    invideo_name = str(videofile).replace("data/", "").replace(".mp4", "")
        # root dir
    result_path = "result/" + str(videofile).replace("data/", "").replace(".mp4", "")
    Path(result_path).mkdir(parents=True, exist_ok=True)

        # txt
    result_txt = result_path + "/bbox.txt"
    f = open(result_txt, 'w')

        # vidoe
    fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')
    result_video = result_path + "/output.mp4"
    traj_video = result_path + "/trajectory.mp4"
    #concat_video = result_path + "/concat.mp4"
    outvideo = cv2.VideoWriter(result_video, fourcc, 20.0, (1280, 720))
    trajvideo = cv2.VideoWriter(traj_video, fourcc, 20.0, (1280, 720))
    #concatevideo = cv2.VideoWriter(concat_video, fourcc, 20.0, (2560, 720))
    # Demi_Edit_End

    while cap.isOpened():
        ret, img = cap.read()   
        sized = cv2.resize(img, (m.width, m.height))
        sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.6, use_cuda) # do_detect 定義於 torch_utils.py
        finish = time.time()
        print('Predicted in %f seconds.' % (finish - start))


        if id == 1:
            trajectory_img = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

        # Demi_Edit_Start => get each frame bounding box center and write to txt file
        point_1x, point_1y = boxes[0][0][0]*1280, boxes[0][0][1]*720
        point_2x, point_2y = boxes[0][0][2]*1280, boxes[0][0][3]*720
        bbox_centerx, bbox_centery = (point_1x + point_2x)/2, (point_1y + point_2y)/2
        print(("frame " + str(id) + " : x_" + str(bbox_centerx) + ", y_" + str(bbox_centery)), file = f)
        # Demi_Edit_End

        # Demi_Edit_Start => save each frame to image
        name = "_frame_" + str(id) + ".jpg"
        name = result_path + "/" + invideo_name + name
        trajname = result_path + "/" + invideo_name + "_traj_" + str(id) + ".jpg"
        #concatname = result_path + "/" + invideo_name + "concat_save_" + str(id) + ".jpg"
        #origname = result_path + "/" + invideo_name + "orig_save_" + str(id) + ".jpg"
        # Demi_Edit_End




        result_img = plot_boxes_cv2(img, boxes[0], savename=name, class_names=class_names)
        cv2.circle(trajectory_img, (int(bbox_centerx), int(bbox_centery)), 3, (255,0,255), -1)
        trajbox_img = plot_basketball_trajectory_bbox(trajectory_img, boxes[0], class_names = class_names)
        concat_img = np.concatenate([result_img, trajbox_img], axis = 1)
        # Demi_Edit_Start => save each frame to video
        cv2.imwrite(trajname, trajbox_img)
        #cv2.imwrite(concatname, concat_img)
        #cv2.imwrite(origname, img)
        outvideo.write(result_img)
        trajvideo.write(trajbox_img)
        #concatevideo.write(concat_img)
        # Demi_Edit_End

        # Demi_Edit_Start => frame id plus
        id = id + 1
        # Demi_Edit_End

        cv2.imshow('Yolo demo', result_img)
        cv2.imshow('traj demo', trajbox_img)
        cv2.waitKey(1)

    cap.release()

def detect_cv2_camera(cfgfile, weightfile):
    import cv2
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if use_cuda:
        m.cuda()

    cap = cv2.VideoCapture(0)

    # give video stream
    # cap = cv2.VideoCapture("./data/Source4.mp4")
    cap.set(3, 1280)
    cap.set(4, 720)
    print("Starting the YOLO loop...")

    num_classes = m.num_classes
    if num_classes == 20:
        namesfile = 'data/voc.names'
    elif num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/x.names'
    class_names = load_class_names(namesfile)


    # Demi_Edit_Start
    # id = 1  # same name num
    # fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')
    # outvideo = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280, 720))
    # Demi_Edit_End

    while cap.isOpened():
        ret, img = cap.read()   
        sized = cv2.resize(img, (m.width, m.height))
        sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.6, use_cuda)
        finish = time.time()
        print('Predicted in %f seconds.' % (finish - start))

        # Demi_Edit_Start
        # name = "save_" + str(id) + ".jpg"
        # id = id + 1
        # Demi_Edit_End

        result_img = plot_boxes_cv2(img, boxes[0], savename=name, class_names=class_names)

        # Demi_Edit_Start
        # outvideo.write(result_img)
        # Demi_Edit_End
        cv2.imshow('Yolo demo', result_img)
        cv2.waitKey(1)

    cap.release()

def get_args():
    parser = argparse.ArgumentParser('Test your image or video by trained model.')
    parser.add_argument('-cfgfile', type=str, default='./cfg/yolov4.cfg',
                        help='path of cfg file', dest='cfgfile')
    parser.add_argument('-weightfile', type=str,
                        default='./checkpoints/Yolov4_epoch1.pth',
                        help='path of trained model.', dest='weightfile')
    parser.add_argument('-imgfile', type=str,
                        default='./data/mscoco2017/train2017/190109_180343_00154162.jpg',
                        help='path of your image file.', dest='imgfile')
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = get_args()
    if args.imgfile:
        # detect_cv2(args.cfgfile, args.weightfile, args.imgfile)
        detect_cv2_video(args.cfgfile, args.weightfile, args.imgfile)
        # detect_imges(args.cfgfile, args.weightfile)
    else:
        detect_cv2_camera(args.cfgfile, args.weightfile)
