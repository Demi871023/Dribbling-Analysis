# PyTorch-TSM

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
    ├── scripts                                                                 some .sh for train or inference for official
    ├── tools
    ├── tsm_fpga
    └── result                                                                  each video with label prediction

## Training Dataset
Assign dataset path in ops/dataset_config.py
```python
def return_datasetname(modality):
    filename_categories = 'dribbling/category.txt'
    if modality == 'RGB':
        root_data = ROOT_DATASET + '/{datasetname}/{datasetname}-frames'
        filename_imglist_train = '{datasetname}/train_videofolder.txt'
        filename_imglist_val = '{datasetname}/valid_videofolder.txt'
        prefix = '{:06d}.jpg'
    elif modality == 'Flow':
        root_data = ROOT_DATASET + ''
        filename_imglist_train = ''
        filename_imglist_val = ''
        prefix = '{:06d}.jpg'
    else:
        raise NotImplementedError('no such modality:'+modality)
    return filename_categories, filename_imglist_train, filename_imglist_val, root_data, prefix
    
    
def return_dataset(dataset, modality):
    dict_single = {'jester': return_jester, 'something': return_something, 'somethingv2': return_somethingv2,
                   'ucf101': return_ucf101, 'hmdb51': return_hmdb51,
                   'kinetics': return_kinetics, 'dribbling': return_dribbling, '{datasetname}': return_datasetname}
```

## Terminal command

### Train Model
    python main.py {dataset root} RGB --arch resnet50 --num_segments 8 --gd 20 --lr {learning rate} --lr_steps 20 40 --epochs {epochs number} --batch-size {batch size number} -j 16 --dropout 0.5 --consensus_type=avg --eval-freq=1 --shift --shift_div=8 --shift_place=blockres --npb
    e.g. python main.py dribbling RGB --arch resnet50 --num_segments 8 --gd 20 --lr 0.01 --lr_steps 20 40 --epochs 50 --batch-size 8 -j 16 --dropout 0.5 --consensus_type=avg --eval-freq=1 --shift --shift_div=8 --shift_place=blockres --npb

### Inference Model
    python test_models.py {dataset root} --weights=pretrained/TSM_something_RGB_resnet50_shift8_blockres_avg_segment8_e45.pth --test_segments=8 --batch_size=72 -j 24 --test_crops=1
    e.g. python test_models.py dribbling --weights=pretrained/ckpt.pth.tar --test_segments=8 --batch_size=72 -j 24 --test_crops=1


## Output
    file output : result/{videoID}_Output.mp4


## Download Weights File
* Fine-tune on dribbling dataset : [download link](https://365nthu-my.sharepoint.com/:u:/g/personal/110062534_office365_nthu_edu_tw/EScmdPbtCf9MgtSRXV7v2YABCIeq3UInKB9Rl32yb46s1w?e=l2a7Pk)
