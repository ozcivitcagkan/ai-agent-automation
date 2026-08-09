gizli_sayi = 42

while True:
    tahmin = input("Bir sayı giriniz: ")

    try:
        tahmin = int(tahmin)
        if tahmin < gizli_sayi:
            print("Daha büyük!")
        elif tahmin > gizli_sayi:
            print("Daha küçük!")
        else:
            print("Tebrikler! Sayıyı buldunuz!")   
            break       

    except ValueError:
        print("Lütfen sayı girin")
