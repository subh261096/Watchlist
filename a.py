import math
n = int(input())
a = 0
b = 1
print(a)
print(b)
for i in range(0, n-2, 1):
    t = a+b
    a = b
    b = t
    print(b)
