
def dosya_oku(dosya_adi):

    try:
        with open(dosya_adi, "r") as dosya:
            icerik = dosya.read()
            return icerik

    except FileNotFoundError:
        print("Dosya bulunamadı")
        return None

print(dosya_oku("notlar.txt"))
print(dosya_oku("terk.txt"))
