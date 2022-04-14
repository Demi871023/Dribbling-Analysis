# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import time
from collections import deque
from operator import itemgetter
from threading import Thread

import cv2
import numpy as np
import torch
from mmcv import Config, DictAction
from mmcv.parallel import collate, scatter

from mmaction.apis import init_recognizer
from mmaction.datasets.pipelines import Compose

# from mmaction.apis import init_recognizer
# from mmaction.datasets.pipelines import Compose

import Configs

HIGHTLOCATION = 0

EXCLUED_STEPS = [
    'OpenCVInit', 'OpenCVDecode', 'DecordInit', 'DecordDecode', 'PyAVInit',
    'PyAVDecode', 'RawFrameDecode'
]

image_recognizer_predict = ""

# Load TSM Official Checkpoints into MMAction2 
def resave_checkpoints(path):
    checkpoint = torch.load(path)
    checkpoint = checkpoint['state_dict']

    preweight = []
    modelweight = []

    # TSM Official
    for key in checkpoint.keys():
        preweight.append(key.replace("module.", ""))

    # MMAction2
    for key in model.state_dict().keys():
        modelweight.append(key)

    base_dict = {'.'.join(k.split('.')[1:]): v for k, v in list(checkpoint.items())}
    replace_dict = {}
    for i in range(len(preweight)):
        replace_dict[preweight[i]] = modelweight[i]     # TSM Official Key, MMAction2

    for k, v in replace_dict.items():
        if k in base_dict:
            base_dict[v] = base_dict.pop(k) #pop 出來 key == k 的 value

    model.load_state_dict(base_dict)
    torch.save(model.state_dict(), 'checkpoints/tsn_r50_256p_1x1x8_100e_kinetics400_rgb.pth')


def visualize():

    cur_time = time.time()
    TEXT_INFO = {}

    while True:
        msg = 'Waiting for action ...'
        ret, frame = camera.read()

        # Frame 沒有被 Capture 的時候就停止
        if ret == False:
            break

        if Configs.connect_state == Configs.CONNECT_STATE_BYE:
            break

        frame_queue.append(np.array(frame[:, :, ::-1]))
        resultPlane = np.zeros((720, 450, 3), np.uint8)


        if len(result_queue) != 0:
            TEXT_INFO = {}
            results = result_queue.popleft()
            SHOW_INFO = {}
            TYPE_RANK = {}

            rank_count = 0
            for type, score in results:             # predicted results is ranking in score
                SHOW_INFO[type] = score
                TYPE_RANK[type] = rank_count
                rank_count = rank_count + 1

            rank_count = 0
            for type in Configs.DRIBBLING_TYPE:
                text = type + " : " + str(SHOW_INFO[type])
                location = (0, 40 + rank_count * 20)
                TEXT_INFO[location] = text
                COLOR = (0, 0, 0)
                if TYPE_RANK[type] == 0 :
                    image_recognizer_predict = type
                    COLOR = Configs.FONT_COLOR_HIGHTLIGHT
                    HIGHTLOCATION = location
                else :
                    COLOR = Configs.FONT_COLOR_NORMAL
                
                cv2.putText(resultPlane, text, location, Configs.FONT_FACE, Configs.FONT_SCALE, 
                            COLOR, Configs.FONT_THICKNESS, Configs.FONT_LINETYPE)
                rank_count = rank_count + 1

                if Configs.user_choosen_dribbling == -1:
                    pass
                elif Configs.user_choosen_dribbling == Configs.DRIBBLING_MAPPING[image_recognizer_predict]:
                    Configs.training_state = Configs.STATE_START
                else:
                    Configs.training_state = Configs.STATE_PAUSE

        elif len(TEXT_INFO) != 0:
            for location, text in TEXT_INFO.items():
                if location == HIGHTLOCATION :
                    cv2.putText(resultPlane, text, location, Configs.FONT_FACE, Configs.FONT_SCALE,
                            Configs.FONT_COLOR_HIGHTLIGHT, Configs.FONT_THICKNESS, Configs.FONT_LINETYPE)
                else :
                    cv2.putText(resultPlane, text, location, Configs.FONT_FACE, Configs.FONT_SCALE,
                            Configs.FONT_COLOR_NORMAL, Configs.FONT_THICKNESS, Configs.FONT_LINETYPE)

        else:
            cv2.putText(resultPlane, msg, (0, 40), Configs.FONT_FACE, Configs.FONT_SCALE, Configs.FONT_COLOR_MSG,
                        Configs.FONT_THICKNESS, Configs.FONT_LINETYPE)

        cv2.imshow('Result Frame', resultPlane)
        cv2.imshow('Camera Frame', frame)
        cv2.waitKey(1)

        if drawing_fps > 0:
            # add a limiter for actual drawing fps <= drawing_fps
            sleep_time = 1 / drawing_fps - (time.time() - cur_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            cur_time = time.time()

    camera.release()
    cv2.destroyAllWindows()

def inference():
    score_cache = deque()
    scores_sum = 0
    cur_time = time.time()

    while True:
        if Configs.connect_state == Configs.CONNECT_STATE_BYE:
            break

        cur_windows = []

        while len(cur_windows) == 0:
            if len(frame_queue) == sample_length:
                cur_windows = list(np.array(frame_queue))
                if data['img_shape'] is None:
                    data['img_shape'] = frame_queue.popleft().shape[:2]

        cur_data = data.copy()
        cur_data['imgs'] = cur_windows
        cur_data = test_pipeline(cur_data)
        cur_data = collate([cur_data], samples_per_gpu=1)
        if next(model.parameters()).is_cuda:
            cur_data = scatter(cur_data, [device])[0]

        with torch.no_grad():
            scores = model(return_loss=False, **cur_data)[0]


        score_cache.append(scores)
        scores_sum += scores

        if len(score_cache) == average_size:
            scores_avg = scores_sum / average_size
            num_selected_labels = min(len(label), 5)
            scores_tuples = tuple(zip(label, scores_avg))
            scores_sorted = sorted(
                scores_tuples, key=itemgetter(1), reverse=True)
            results = scores_sorted[:num_selected_labels]
            result_queue.append(results)
            scores_sum -= score_cache.popleft()

        if inference_fps > 0:
            # add a limiter for actual inference fps <= inference_fps
            sleep_time = 1 / inference_fps - (time.time() - cur_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            cur_time = time.time()


def image_recognizer_main():
    global frame_queue, camera, frame, results, threshold, sample_length,\
        data, test_pipeline, model, device, average_size, label, dribbling_type,\
        result_queue, drawing_fps, inference_fps

    # # Args Setting
    average_size = Configs.AVERAGE_SIZE
    threshold = Configs.THRESHOLD
    drawing_fps = Configs.DRAWING_FPS
    inference_fps = Configs.INFERENCE_FPS
    device = torch.device(Configs.DEVICE)
    cfg = Config.fromfile(Configs.MODEL_CONFIG)
    model = init_recognizer(cfg, Configs.CHECKPOINT, device = device)
    data = dict(img_shape = None, modality = 'RGB', label = -1)
    with open(Configs.LABEL, 'r') as f:
        label = [line.strip() for line in f]

    # prepare test pipeline from non-camera pipeline
    cfg = model.cfg
    sample_length = 0
    pipeline = cfg.data.test.pipeline
    pipeline_ = pipeline.copy()
    for step in pipeline:
        if 'SampleFrames' in step['type']:
            sample_length = step['clip_len'] * step['num_clips']
            data['num_clips'] = step['num_clips']
            data['clip_len'] = step['clip_len']
            pipeline_.remove(step)
        if step['type'] in EXCLUED_STEPS:
            pipeline_.remove(step)
    test_pipeline = Compose(pipeline_)

    assert sample_length > 0

    frame_queue = deque(maxlen = sample_length)
    result_queue = deque(maxlen=1)

    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
