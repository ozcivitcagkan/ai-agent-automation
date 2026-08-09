sinav_notu = input("Notunuzu giriniz: ")

sinav_notu = int(sinav_notu)

if sinav_notu < 0 or sinav_notu > 100:
    print("Geçersiz not girdiniz")
elif sinav_notu >= 85:
    print("Harika! AA aldın")
elif sinav_notu >= 70 or sinav_notu <= 84 :
    print("İyi! BA aldın")
elif sinav_notu >= 50 or sinav_notu <= 69 :
    print("Geçtin, CB aldın")
else :
    print("Kaldın, tekrar dene")



