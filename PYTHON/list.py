
alisveris = []

while True:
    urun = input("Listeye eklemek istediğin ürün :  (çıkmak için 'q' yaz) ")

    if urun != 'q' :
        alisveris.append(urun)
    else:
        break

for i, urun in enumerate(alisveris):
    print(i + 1, urun)