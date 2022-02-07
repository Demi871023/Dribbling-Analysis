# UI_ClipAndVisualize

    > Based On Openpose and YOLOv4 Environment


## Directory Structure

    .
    ├── README.md
    ├── main.py                                                                 train model
    ├── test_models.py                                                          inference model
    ├── opts.py                                                                 define some argparse
    ├── archs
    │   ├── bn_inception.py
    │   └── mobilenet_v2.py
    ├── dataset
    │   └── dribbling                                                           basketball dribbling dataset
    ├── log
    │   ├── TSM_dribbling_RGB_resnet50_shift8_blockres_avg_segment8_e2          log file in per model training
    │   ├── plot_result.py                                                      visualize model testing acc and loss
    │   └── ResultFig.png                                                       result .png file
    ├── ops
    │   ├── basic_ops.py
    │   ├── dataset.py
    │   ├── dataset_config.py                                                   dataset path setting
    │   ├── models.py
    │   ├── non_local.py
    │   ├── temporal_shift.py
    │   ├── transforms.py
    │   └── utils.py
    ├── scripts                                                                 
    ├── openpose.py
    ├── yolov4.py
    └── ui.py                                                                  each video with label prediction



## How to use
<img src="https://i.imgur.com/bkB06cv.png">