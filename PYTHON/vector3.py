import math

def vektor_uzunluk(a):
    toplam = 0

    for i in range(len(a)):
        toplam = toplam + (a[i] ** 2)

    
    return math.sqrt(toplam)


print(vektor_uzunluk([3,4]))

