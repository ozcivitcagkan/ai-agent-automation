import numpy as np

# a = np.array([1, 2, 3, 4])

# print(a)
# print(type(a))

# a = np.array([[1, 2, 3],
#              [4, 5, 6]])

# print(a.shape)

# print(np.zeros(5))
# print(np.ones((2, 3)))
# print(np.arange(0, 10, 2))
# print(np.random.rand(3))


# a = np.array([1, 2, 3])
# b = np.array([4, 5, 6])

# print(a * b)
# print(a + b)
# print(np.dot(a, b))

# notlar = np.array([70, 85, 60, 95, 40])

# # 40 60 70 85 95

# print(notlar.mean())
# print(np.median(notlar))
# print(notlar.std())
# print(notlar.var())
# print(notlar.sum())
# print(notlar.min())
# print(notlar.max())

# a = np.array([10, 20, 30, 40, 50])

# print(a[0])       
# print(a[-1])     
# print(a[1:4])     
# print(a[:3])    
# print(a[2:])      


# m = np.array([[1, 2, 3],
#               [4, 5, 6]])

# print(m[0, 1])
# print(m[0])    
# print(m[:, 1])  


# a = np.array([1, 2, 3])
# b = np.array([4, 5, 6])

# print(a + b)
# print(np.dot(a, b))
# print(np.linalg.norm(a))


# sinif_A = np.array([68, 70, 72, 70, 70])
# sinif_B = np.array([20, 100, 45, 95, 90])


# print(sinif_A.mean())
# print(sinif_B.mean())
# print(sinif_A.std())
# print(sinif_B.std())


# notlar = np.array([45, 78, 92, 33, 67, 88, 51, 95])

# print(notlar[notlar > 70])
# print(len(notlar[notlar > 70]))
# print((notlar[notlar > 70]).mean())


m = np.array([[1, 2, 3],
              [4, 5, 6]])


print(m.shape)
print(m.T)
print(m[:, 1])