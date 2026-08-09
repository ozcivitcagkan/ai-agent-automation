sepet = [
    {"urun": "Ekmek", "fiyat": 15},
    {"urun": "Süt", "fiyat": 35},
    {"urun": "Peynir", "fiyat": 80},
    {"urun": "Yumurta", "fiyat": 45}
]
toplam = 0
# for i in sepet:
#     print(f"{i['urun']}: {i['fiyat']}")

for i in sepet:
    toplam = toplam + i["fiyat"]

print(toplam)