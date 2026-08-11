m = [
    [1, 2, 3],  [4, 5, 6]
     ]

# print(m[0][0], m[1][0])
# print(m[0][1], m[1][1])
# print(m[0][2], m[1][2])


 # [1, 4]
 # [2, 5]
 # [3, 6] 3 satır 2 sütun

def transpoze(m):
    yeni = []

    for j in range(len(m[0])):
        satir = []
        for i in range(len(m)):
            satir.append(m[i][j])
        yeni.append(satir)

    return yeni
