a = [1,2,3,4,5,6]

a[:len(a)//2], a[len(a)//2:] = a[len(a)//2:], a[:len(a)//2]

print(a)