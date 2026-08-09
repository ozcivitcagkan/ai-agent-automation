
class Araba:
    def __init__(self, marka, model):
        self.marka = marka
        self.model = model
        self.hiz = 0

    def hizlan(self, miktar):
        self.hiz = self.hiz + miktar

    def bilgi_goster(self):
        print(f"Marka : {self.marka}   Model : {self.model}   Hız : {self.hiz}")


araba1 = Araba("Toyota", "Corolla")
araba1.bilgi_goster()      # Marka : Toyota Model : Corolla Hız : 0

araba1.hizlan(50)
araba1.bilgi_goster()      # Marka : Toyota Model : Corolla Hız : 50

araba1.hizlan(30)
araba1.bilgi_goster()      # Marka : Toyota Model : Corolla Hız : 80

araba2 = Araba("Citroen", "C4")
araba2.bilgi_goster()

araba2.hizlan(60)
araba2.bilgi_goster()

araba2.hizlan(30)
araba2.bilgi_goster()