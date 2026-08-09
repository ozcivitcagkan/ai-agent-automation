import random

gizli_sayi = random.randint(1,100)

try:
    while True:
        sayi = input("Bir sayı giriniz: ")
        sayi = int(sayi)

        if sayi < gizli_sayi:
            print("Daha büyük!")
        elif sayi > gizli_sayi:
            print("Daha küçük!")
        else:
            print("Tebrikler, sayıyı buldunuz!")
            break

except ValueError:
    print("Lütfen bir sayı girin")
