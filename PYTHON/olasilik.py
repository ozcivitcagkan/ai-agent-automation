
def hata_hesapla(tahminler, gercekler):
    toplam = 0

    for i in range(len(tahminler)):
        toplam = toplam + (tahminler[i] - gercekler[i]) ** 2
    return toplam / len(tahminler)



print(hata_hesapla([10, 20, 30], [12, 18, 33]))