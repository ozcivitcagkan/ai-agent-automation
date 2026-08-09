import random

kelimeler = ["elma", "kitap", "bilgisayar", "güneş", "deniz"]

kelime= random.choice(kelimeler)

liste = list(kelime)
random.shuffle(liste)
karisik_kelime = "".join(liste)  
print(karisik_kelime)

while True:
    tahmin = input(f"Karışık kelime : {karisik_kelime}, sizin tahmininiz: ")

    if tahmin == kelime:
        print("Doğru!")
        break
    else:
        print("Tekrar dene!")