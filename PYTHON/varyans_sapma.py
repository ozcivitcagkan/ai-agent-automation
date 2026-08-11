import math

sinif_A = [68, 70, 72, 70, 70]

def varyans(a):
    toplam = 0
    for i in a:
        toplam = toplam + i
    ortalama =  toplam / len(a)

    kare_toplami_terk = 0
    for i in a:
        kare_toplami_terk = kare_toplami_terk + (i - ortalama) ** 2

    return kare_toplami_terk / len(a)

def standart_sapma(a):
    return math.sqrt(varyans(a))

print(varyans(sinif_A))
print(standart_sapma(sinif_A) * 3)



    

