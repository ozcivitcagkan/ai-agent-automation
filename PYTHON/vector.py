
def vektor_topla(a, b):
    sonuc = []

    for i in zip(a, b):
        sonuc.append(a[i] + b[i])

    return sonuc

print(vektor_topla([1, 2, 3], [4, 5, 6]))
