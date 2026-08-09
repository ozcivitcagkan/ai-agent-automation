
while True:
    not_metin = input("Not gir (çıkmak için 'q'): ")

    if not_metin == 'q':
        break

    with open("notlar.txt", "a") as dosya:
        dosya.write(not_metin + "\n") 

with open("notlar.txt", "r") as dosya:
    for satir in dosya:
        print(satir.strip()) 
