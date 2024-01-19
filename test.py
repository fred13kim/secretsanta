#!/usr/bin/python3
import numpy as np

list = []

for i in range(60):
    list.append(i)
print(list)
print("")

width = 6
height = 10

list = np.reshape(list,(width,height))
list1 = list[::2]
list2 = np.fliplr(list[1::2])

list[::2] = list1
list[1::2] = list2

list = np.reshape(list,60)
print(list)
