gizli_sayi = 17

while True:
    tahmin = input("Bir sayı giriniz: ")
    tahmin = int(tahmin)

    if (tahmin < gizli_sayi):
      print("Daha büyük bir sayı giriniz.")
    elif (tahmin > gizli_sayi):
      print("Daha küçük bir sayı giriniz.")
    else :
      print("Tebrikler, bildiniz!")
      break
    

