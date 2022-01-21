# Dribbling Dataset

## Directory Structure

    .
    ├── README.md
    ├── vid2img_dribbling.py            extra frame image from video
    ├── gen_label_dribbling.py          genearte dataset-labels.json
    ├── json_prepare.py                 generate dataset-train.json, dataset-test.json, dataset-valid.json
    ├── train_videofolder.txt           training data list
    ├── test_videofolder.txt            test data list
    ├── valid_videofolder.txt           valid data list
    ├── test_list.txt
    ├── dribbling-labels.json           dataset label json file
    ├── dribbling-train.json            training data each data id and label
    ├── dribbling-test.json             test data each data id and label
    ├── dribbling-valid.json            valid data each data id and label
    ├── dribbling-video
    │   ├── 1.mp4
    │   ├── 2.mp4
    │   ├── ....
    │   └── N.mp4
    └──dribbling-frames
        ├── 1
        │   ├── 000001.jpg
        │   ├── 000002.jpg
        │   ├── ...   
        │   └── 00000N.mp4
        ├── 2
        │   ├── 000001.jpg
        │   ├── 000002.jpg
        │   ├── ...   
        │   └── 00000N.mp4
        ├── ....
        └── N
            ├── 000001.jpg
            ├── 000002.jpg
            ├── ...   
            └── 00000N.mp4
            
## JSON File

### dribbling-train.json
```python
[
    {"id": "193", "label": "behind dirbble"}, 
    {"id": "123", "label": "behind dirbble"}, 
    ...
    {"id": "182", "label": "behind dirbble"}, 
    {"id": "194", "label": "behind dirbble"},
]
```

### dribbling-test.json
```python
[
    {"id":"2355"}
]
```

### dribbling-valid.json
```python
[
    {"id": "7", "label": "behind dirbble"}, 
    {"id": "11", "label": "behind dirbble"}, 
    ...
    {"id": "15", "label": "behind dirbble"}, 
    {"id": "21", "label": "behind dirbble"},
]
```
## TXT File Format
    videoID frameCount labelID
