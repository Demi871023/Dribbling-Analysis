from matplotlib import pyplot as plt
import csv

plot_loss = []
plot_acc = []

log_root = "TSM_dribbling_RGB_resnet50_shift8_blockres_avg_segment8_e15/"

# 讀進 csv
csv_path = log_root + "log.csv"

with open(csv_path, newline='') as csvfile:
    rows = csv.reader(csvfile)
    # 以迴圈輸出每一列
    for row in rows:
        # 空白行
        if(len(row) == 0):
            continue
    
        # print(row[0])
        # print("@@@@@@@@@@@@@@@@@@@@@@")
        if "Testing Results: " in row[0]:
            line = row[0]
            split_item = line.split(" ", -1)
            plot_loss.append(float(split_item[7]))
            plot_acc.append(float(split_item[3]))


# plot
epoch = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
plt.figure(figsize=(15,10),dpi=100,linewidth = 2)
plt.subplot(1,2,1)
plt.plot(epoch,plot_loss,'-',color = 'r', label="loss")
plt.title("TSM Training on Dribbling Loss", fontproperties="SimHei")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel("epoch", fontsize=12)
plt.ylabel("loss", fontsize=12)
# plt.legend(loc = "best", fontsize=20)
plt.subplot(1,2,2)
plt.plot(epoch,plot_acc,'-',color = 'r', label="accuracy")
plt.title("TSM Training on Dribbling Accuracy", fontproperties="SimHei")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel("epoch", fontsize=12)
plt.ylabel("accuracy", fontsize=12)
plt.savefig('Output_Fig.png')
plt.show()

print(plot_loss)
print(plot_acc)