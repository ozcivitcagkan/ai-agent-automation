import os
import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

vo = voyageai.Client()

dokumanlar = [
    "Kedi kanepede uyuyor",
    "Kedi koltukta uyukluyor",
    "Borsa bugün düştü"
]

sonuc_dokuman = vo.embed(
    dokumanlar,
    model="voyage-4",
    input_type="document"
)

dokuman_embeddingleri = sonuc_dokuman.embeddings

soru = "Kedilerle ilgili bir cümle bul"

sonuc_soru = vo.embed(
    [soru],
    model="voyage-4",
    input_type="query"
)

soru_vektor = sonuc_soru.embeddings[0]


def kosinus_benzerlik(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


for i, dokuman_vektoru in enumerate(dokuman_embeddingleri):
    skor = kosinus_benzerlik(soru_vektor, dokuman_vektoru)

    # print(f"{skor:.4f} -> {dokumanlar[i]}")

testler = [
    "Kedi kanepede uyuyor",
    "Bugün hava çok yağmurlu",
    "Araba çok hızlı gidiyor",
    "Otomobil yüksek sürat yapıyor"
]

sonuc = vo.embed(
    testler,
    model="voyage-4",
    input_type="document"
)

v1 = sonuc.embeddings[0]
v2 = sonuc.embeddings[1]
v3 = sonuc.embeddings[2]
v4 = sonuc.embeddings[3]

print("E2 - Alakasız:", kosinus_benzerlik(v1, v2))
print("E3 - Anlamca benzer:", kosinus_benzerlik(v3, v4))