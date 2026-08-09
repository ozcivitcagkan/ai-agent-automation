alisveris=[]

while True:
    urun = input("Ürün giriniz: (q ile çıkın)")

    if urun == 'q':
        break
    alisveris.append(urun)

    with open("alisveris.txt", "a") as terk:
        terk.write(urun + "\n")

with open("alisveris.txt","r") as terk:
    for satir in terk:
        print(satir.strip())





