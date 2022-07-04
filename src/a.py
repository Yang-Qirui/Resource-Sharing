import numpy as np
import random

arr = []
m = 4
n = 7
c = 3
for _ in range(m):
    tag = random.sample(range(0, n), c)
    tmp = []
    for i in range(n):
        if i in tag:
            tmp.append(1)
        else:
            tmp.append(0)
    arr.append(tmp)

A = np.array(arr)

B = np.array(['1101', '2202'])
print(A)
print(B)
print(bin(int('101', 2) ^ int('010', 2))[2:])
# print(np.linalg.det(A))
