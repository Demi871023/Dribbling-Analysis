# Tactics Tools
  > Base on Tactics Trajecotry Database
  > Can do : (1) Draw Trajecotry (2) Parser Court Athena .json File, (3) Transfer to Unity Coordinate


### Directory Structure

    .
    ├── README.md
    ├── main.py                                                                 train model
    ├── parser.py
    ├── visualize.py
    ├── coordinate.py
    ├── config.py
    ├── TACTICSDB_CLASSIFICATION
    │   ├── Player 1
    │   ├── Player 2
    │   ├── Player 3
    │   ├── Player 4
    │   └── Player 5
    ├── TACTICSDB
    │   ├── 0_04.FIRST.91.BOX.npy
    │   ├── 0_04.FLOPPY.12.HAWK.py
    │   ...
    │   └── 11)PUNCH.15.MOTION.GIVE.npy
    ├── JSONSOURCE                                                                 
    └── DESTINATION
        ├── PARSER
        ├── Visualize
        └── COORDINATE



### How to run
```
python main.py -m [DT/PJ/TC] -c [config file] -s [source path] -d [destination path]
```

### Visualize Trajecotry

### Parser Court Athena .json File

### Transfer to Unity Coordinate




### Resource
* [TACTICSDB DOWNLOAD](https://365nthu-my.sharepoint.com/:u:/g/personal/110062534_office365_nthu_edu_tw/EZzc5UCJwg1KpKpVeBId-eMB0wrnaIgxpihlwSK6Xx4x4w?e=wz5eD3)
