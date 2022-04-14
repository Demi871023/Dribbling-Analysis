from itertools import count
from operator import itemgetter


with open('0.txt') as f,  open('1.txt') as b, open("2.txt", "w") as c:
    lines = f.readlines()
    blines = b.readlines()
    print(len(lines))
    print(len(blines))
    for i in range(len(lines)):
        str = lines[i].replace("\n", "")
        bstr = blines[i].replace("\n", "")
        itmes = str.split(",")
        bitmes = bstr.split(",")
        newline = itmes[0] + "," + itmes[1] + "," + bitmes[2] + "," + bitmes[3] + "," + itmes[4] + "," + itmes[5] + "," + itmes[6]
        # print(newline)
        c.write(newline + "\n")