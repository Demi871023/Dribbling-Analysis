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

#### Input JSON Format Example

  ```json
  [
    {
      "duration":2,
      "eventType":"空檔",
      "labels":[
        {
          "name":"選手",
          "type":"選手",
          "value":"Bn1GSD4zuo"
        }
      ],
      "startFrame":0,
      "firebaseKey":"-MxUAqNJxHGlZXveZpuF"
    },
  ]
  ```

#### Output File Format Example
  
  ```
  20                                      → steps in this tactics
  5                                       → the 1st frame who is free, for example : the 5 player is free in 1st frame
  5
  4
  4
  4                                       → the 5st frame who is free, for example : the 4 player is free in 8st frame
  -1                                      → -1 is meaning that no player is free in this frame
  -1
  -1
  -1
  -1
  -1
  2
  2
  2
  2
  2
  2,3                                     → the 17st frame who is free, for example : the 2 or 3 player is free in 17st frame
  2,3
  2,3
  2,3
  0,1,2,3,4,11,12,13,14,15,16,17,18,19    → which frames is have free player
  ```

### Transfer to Unity Coordinate

#### Tactic Coordinate and Unity Coordinate
![image](https://github.com/Demi871023/Dribbling-Analysis/blob/main/Tactics%20Tools/PICTURE/TCIMG2.png)



### Resource
* [TACTICSDB DOWNLOAD](https://365nthu-my.sharepoint.com/:u:/g/personal/110062534_office365_nthu_edu_tw/EZzc5UCJwg1KpKpVeBId-eMB0wrnaIgxpihlwSK6Xx4x4w?e=wz5eD3)
