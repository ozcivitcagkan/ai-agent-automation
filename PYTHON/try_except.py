
sayi = input("Bir sayı giriniz: ")


try:
    sayi = int(sayi)

    if sayi < 0 or sayi > 100:
        print("Geçersiz not aralığı")     
    elif sayi >= 85:
        print("Harika! AA aldın")
    elif sayi >= 69 or sayi < 85:
        print("İyi! BA aldın")
    elif sayi >= 50 or sayi < 69:
        print("Geçtin, CB aldın")
    else:
        print("Kaldın, tekrar dene")

except ValueError:
        print("Geçersiz giriş, sayı girmelisiniz")


