from tool.utils import *
from tool.torch_utils import *
from tool.darknet2pytorch import Darknet
import argparse
from tool.draw_trajectory import *
from pathlib import Path
import cv2

use_cuda = True


def detect_cv2(m, img, class_names):

    sized = cv2.resize(img, (m.width, m.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.6, use_cuda)
        finish = time.time()

    point_1x, point_1y = boxes[0][0][0]*1280, boxes[0][0][1]*720
    point_2x, point_2y = boxes[0][0][2]*1280, boxes[0][0][3]*720
    bbox_centerx, bbox_centery = (point_1x + point_2x)/2, (point_1y + point_2y)/2

    # img = plot_boxes_cv2(img, boxes[0], savename=None, class_names=class_names)
    return bbox_centery, boxes