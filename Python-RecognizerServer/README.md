# Python-RecognizerServer

  > this is recognizer server for dribbling base on image or imu sensor

## Directory Structure

    .
    ├── README.md
    ├── Server.py                                                                 train model
    ├── Configs.py                                                          inference model
    ├── ImageRecognizer.py                                                                 define some argparse
    ├── configs
    │   ├── _base_
    │   ├── temporal_shift.py
    │   ├── transforms.py
    │   └── recognition
    ├── scripts                                                                 some .sh for train or inference for official
    ├── tools
    ├── tsm_fpga
    └── result                                                                  each video with label prediction
