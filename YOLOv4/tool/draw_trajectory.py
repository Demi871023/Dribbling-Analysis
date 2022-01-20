import sys
import os
import time
import math
import numpy as np
import cv2

import itertools
import struct  # get_image_size
import imghdr  # get_image_size


def plot_basketball_trajectory(img, bbox_x, bbox_y):
    colors = np.array([[1, 0, 1], [0, 0, 1], [0, 1, 1], [0, 1, 0], [1, 1, 0], [1, 0, 0]], dtype=np.float32)

    point_size = 1
    point_color = (255, 255, 255)
    thickness = 0

    width = img.shape[1]
    height = img.shape[0]
    blank_img = np.zeros((height, width, 3), np.uint8)
    cv2.circle(blank_img, (int(bbox_x), int(bbox_y)), point_size, point_color, thickness)

    return blank_img

def plot_basketball_trajectory_bbox(img, boxes, class_names = None, color=None):
    import cv2
    img = np.copy(img)
    colors = np.array([[1, 0, 1], [0, 0, 1], [0, 1, 1], [0, 1, 0], [1, 1, 0], [1, 0, 0]], dtype=np.float32)

    def get_color(c, x, max_val):
        ratio = float(x) / max_val * 5
        i = int(math.floor(ratio))
        j = int(math.ceil(ratio))
        ratio = ratio - i
        r = (1 - ratio) * colors[i][c] + ratio * colors[j][c]
        return int(r * 255)

    width = img.shape[1]
    height = img.shape[0]
    for i in range(len(boxes)):
        box = boxes[i]
        x1 = int(box[0] * width)
        y1 = int(box[1] * height)
        x2 = int(box[2] * width)
        y2 = int(box[3] * height)

        if color:
            rgb = color
        else:
            rgb = (255, 0, 0)
        if len(box) >= 7 and class_names:
            cls_conf = box[5]
            cls_id = box[6]
            print('%s: %f' % (class_names[cls_id], cls_conf))
            classes = len(class_names)
            offset = cls_id * 123457 % classes
            red = get_color(2, offset, classes)
            green = get_color(1, offset, classes)
            blue = get_color(0, offset, classes)
            if color is None:
                rgb = (red, green, blue)
            # img = cv2.putText(img, class_names[cls_id], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,0), 2)
        img = cv2.rectangle(img, (x1, y1), (x2, y2), (255,255,0), 2)
    return img