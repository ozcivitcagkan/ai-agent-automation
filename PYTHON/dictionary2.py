ogrenciler = [
    {"isim": "Ali", "not": 85},
    {"isim": "Ayşe", "not": 92},
    {"isim": "Mehmet", "not": 67}
]

toplam = 0    

for ogrenci in ogrenciler:
    print(f"{ogrenci['isim']}: {ogrenci['not']}")
    toplam = toplam + ogrenci["not"]   

ortalama = toplam / len(ogrenciler)    
print(f"Sınıf ortalaması: {ortalama}")