import json
import os
from random import sample


# 先讀入少於 8 frame 的影片號碼
lowfile = open("low.txt", "r")
lowlist = []
for line in lowfile:
    lowlist.append(line.replace("\n", ""))

# 讀入所有的 frame，按照類別排序好
os.chdir("dribbling-frames")
dataset = {"behind-list":[], "pound-list":[], "cross over-list":[], "one side leg-list":[]}
# behindlist, poundlist, crossoverlist, onesideleglist = [], [], [], []
for f in os.listdir():
    dele = False
    for element in lowlist:
        if(int(f) == int(element)):
            # print(f)
            dele = True
            break
    
    if(dele == False):
        if( int(f) >= 1 and int(f) <= 243 ):        # 背後 1 - 243
            dataset.get("behind-list").append(int(f))
            dataset.get("behind-list").sort()
        elif( int(f) >= 244 and int(f) <= 1229 ):   # 單手 244 - 1229
            dataset.get("pound-list").append(int(f))
            dataset.get("pound-list").sort()
        elif( int(f) >= 1230 and int(f) <= 1622 ):  # 換手 1230 - 1622
            dataset.get("cross over-list").append(int(f))
            dataset.get("cross over-list").sort()
        elif( int(f) >= 1623 and int(f) <= 2346):   # 跨下 1623 - 2346
            dataset.get("one side leg-list").append(int(f))
            dataset.get("one side leg-list").sort()

os.chdir("..")

# 寫出成多個 json 檔案
def writeToJSONFile(path, fileName, data):
    filePathNameWExt = fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)

def list_splitter(list_to_split, ratio):
    total_elements = len(list_to_split)
    train_elements = (total_elements * ratio)
    train_list = sample(list_to_split, int(total_elements * ratio))
    # middle = int(elements * ratio)
    valid_list = []

    for i in list_to_split:
        if(i not in train_list):
            valid_list.append(i)

    print(train_list)
    print(valid_list)
    print("\n")


    return [train_list, valid_list]

# def TrainTestJSON(path, fileName, data):
#     aList = [{"a":54, "b":87}, {"c":81, "d":63}, {"e":17, "f":39}]



#dribbling-labels.json
labels = ["behind", "pound", "cross over", 'one side leg']
data, idx = {}, 0
for element in labels:
    data[element + " dirbble"] = str(idx)
    idx = idx + 1

writeToJSONFile('', 'dribbling-labels', data)


#dribbling-train.json, dribbling-test.json
datasetsplit_type = {}
datasetsplit_train = []
datasetsplit_test = []
datasetsplit_valid = []


for label in labels:
    splitlist = label + "-list"
    splittrain = label + "-train"
    splittest = label + "-test"

    train, valid = list_splitter(dataset.get(splitlist), 0.7)
    # print(train)

    # print(valid)

    for id in train:
        train_pair = {"id": str(id), "label": label + " dirbble"}
        datasetsplit_train.append(train_pair.copy())
        # print(train_pair)


    # print("=========================")
    # for id in test:
    #     test_pair = {"id": str(id)}
    #     datasetsplit_test.append(test_pair.copy())

    for id in valid:
        valid_pair = {"id" : str(id), "label": label + " dirbble"}
        datasetsplit_valid.append(valid_pair.copy())
        # print(valid_pair)
        


    writeToJSONFile('', 'dribbling-train', datasetsplit_train)
    writeToJSONFile('', 'dribbling-test', datasetsplit_test)
    writeToJSONFile('', 'dribbling-valid', datasetsplit_valid)

    tmp = {splittrain:train, splittest:valid}
    datasetsplit_type.update(tmp)

# print(datasetsplit_train)
# print("=============")
# print(datasetsplit_test)
    

