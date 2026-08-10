def nokta_carpim(a, b):
    toplam = 0
    for i in range(len(a)):
        toplam = toplam + (a[i] * b[i])
    return toplam


ali = [5, 1, 4]
ayse = [4, 2, 5]
mehmet = [1, 5, 1]


skor1 = nokta_carpim(ali, ayse)
skor2 = nokta_carpim(ali, mehmet)

print(skor1)
print(skor2)

if skor1 > skor2:
    print("Ali, Ayşe'ye daha çok benziyor")
else:
    print("Ali, Mehmet'e daha çok benziyor")