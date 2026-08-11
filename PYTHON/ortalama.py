sinif_A = [68, 70, 72, 70, 70]     
sinif_B = [20, 100, 45, 95, 90]     

def ortalama(a):
    toplam = 0
    for i in a:
        toplam = toplam + i
    return toplam / len(a)

print(ortalama(sinif_A))
