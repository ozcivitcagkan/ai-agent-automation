def sepet_toplami(urunler):
    toplam = 0
    for i in urunler:
        toplam = toplam + i["fiyat"]
    return toplam

sepet = [
    {"urun": "Ekmek", "fiyat": 15},
    {"urun": "Süt", "fiyat": 35},
    {"urun": "Peynir", "fiyat": 80},
    {"urun": "Yumurta", "fiyat": 45}
]

toplam = sepet_toplami(sepet)
print(f"Toplam: {toplam} TL")
