
import numpy as np
from outliers import smirnov_grubbs as grubbs
import pandas as pd
# def reject_outliers2(data, m=3):
#     return data[abs(data - np.mean(data)) < m * np.std(data)]
import statistics


# array = [6000000, 6500000, 8300000,6500000,8000000,7000000, 4000000, 5000000, 7000000,8600000]
# sorted(array)
# newarray = []
# for i in array

def reject_outliers(data, m = 4):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]


original_list = [6000000, 6500000, 4100000, 520000,  6500000, 4000000, 4700000]
percent = 1.35
resulting_list = []
limit = None

for number in sorted(original_list):
    if not limit or number > limit:
        limit = number*percent
        sublist = [number]
        resulting_list.append(sublist)
    else:
        sublist.append(number)


def getMeanPrice(data):

    max_ = max(data)
    min_ = min(data)
    mean = round(statistics.mean(data))

    return [min_, max_, mean]



for i in resulting_list:
    print(getMeanPrice(i))

