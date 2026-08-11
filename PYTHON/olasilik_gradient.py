def hata_hesapla(tahminler, gercekler):
    toplam = 0

    for i in range(len(tahminler)):
        toplam = toplam + (tahminler[i] - gercekler[i]) ** 2
    return toplam / len(tahminler)

x_degerleri = [1, 2, 3, 4]
y_degerleri = [2, 4, 6, 8]
a = 0


for tur in range(20):
    tahminler = []
    for x in x_degerleri:
        tahminler.append(a * x)

    hata = hata_hesapla(tahminler, y_degerleri)
    print(f"a = {a}, hata = {hata}")

    a = a + 0.2