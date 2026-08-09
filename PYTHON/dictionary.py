rehber = {}

while True:
    isim = input("İsim gir (çıkmak için 'q'): ")

    if isim == 'q':
        break

    telefon = input("Telefon numarası: ")
    rehber[isim] = telefon 


for isim, telefon in rehber.items():
    print(f"{isim}: {telefon}")