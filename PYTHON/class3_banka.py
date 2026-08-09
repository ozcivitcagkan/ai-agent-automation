class BankaHesabi:
    def __init__(self, isim):
        self.isim = isim
        self.bakiye = 0

    def para_yatir(self,miktar):
        self.bakiye += miktar

    def para_cek(self, miktar):
        if miktar > self.bakiye:
            print("Yetersiz bakiye!")
        else:
            self.bakiye -= miktar

    def bakiye_goster(self):
        print(f"Bakiye : {self.bakiye} €")

hesap1 = BankaHesabi("Ali")
hesap1.bakiye_goster()

hesap1.para_yatir(100)
hesap1.bakiye_goster()

hesap1.para_yatir(200)
hesap1.bakiye_goster()

hesap1.para_cek(100)
hesap1.bakiye_goster()

hesap1.para_cek(300)
hesap1.bakiye_goster()