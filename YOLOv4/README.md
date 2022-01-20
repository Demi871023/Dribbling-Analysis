# Pytorch-YOLOv4

## Directory Structure

    .
    ├── README.md
    ├── dataset.py                      dataset
    ├── demo.py                         demo to run pytorch
    ├── models.py                       model for pytorch
    ├── train.py                        train models.py
    ├── cfg
    │   ├── yolov4.cfg                  official config
    │   └── yolov4-obj.cfg              fine-tune config
    ├── data
    │   ├── coco.names                  coco dataset label
    │   ├── voc.names                   voc dataset label
    │   └── x.names                     fine-tune label
    ├── weight
    │   ├── yolov4.weights              official weights
    │   └── yolov4_finetune.weights     fine-tune weights
    ├── tool
    │   ├── camera.py                   a demo camera
    │   ├── coco_annotation.py          coco dataset generator
    │   ├── config.py
    │   ├── darknet2pytorch.py
    │   ├── region_loss.py
    │   ├── utils.py
    │   └── yolo_layer.py
    └── result                          output


## Recommended version
pytorch 1.7.1+cu101

## Terminal command
    python demo.py -cfgfile <cfg_file> -weightfile <weights_file> -imgfile <video_file>
    e.g. python demo.py -cfgfile cfg/yolov4-obj.cfg -weightfile weights/yolov4_finetune.weights -imgfile data/SH_Source6_R.mp4

## Output
    terminal output : basektball bounding box coordinate (x1, y1, x2, y2)
    
    file output : 
    result/<video_file>/bbox.txt : each frame basketball center coordinate (x, y)
    result/<video_file>/output.mp4 : input video with bounding box visualize
    result/<video_file>/{<video_file>_frame_{id}}.jpg : each frame with bounding box visualize
    result/<video_file>/{<video_file>_traj_{id}}.jpg : each frame only bounding box visualize and basektball center visualize
    
## Download Weights File
* [yolov4.weights]()
* [yolov4_finetune.weights]()


