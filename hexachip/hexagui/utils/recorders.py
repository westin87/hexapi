import time


def receive_mag_data(self, raw_mag_data):
    mag_data = eval(raw_mag_data)
    timestamp = time.strftime("%y%m%d%H%M%S")
    with open("mag_data_{}.txt".format(timestamp), mode='a') as fo:
        fo.write("{}\n".format(mag_data))
    print("Mag: {}".format(mag_data))


def receive_acc_data(self, raw_acc_data):
    acc_data = eval(raw_acc_data)
    timestamp = time.strftime("%y%m%d%H%M%S")
    with open("acc_data_{}.txt".format(timestamp), mode='a') as fo:
        fo.write("{}\n".format(acc_data))
    print("Acc: {}".format(acc_data))


def receive_ang_data(self, raw_acc_data):
    acc_data = eval(raw_acc_data)
    timestamp = time.strftime("%y%m%d%H%M%S")
    with open("ang_data_{}.txt".format(timestamp), mode='a') as fo:
        fo.write("{}\n".format(acc_data))
    print("Ang: {}".format(acc_data))
