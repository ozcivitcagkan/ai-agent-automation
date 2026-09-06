import os
import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

vo = voyageai.Client()

def sabit_boyutlu_chunk(metin, chunk_boyutu=200):
    chunklar = []

    for i in range(0, len(metin), chunk_boyutu):
        chunklar.append(metin[i:i + chunk_boyutu])

    return chunklar


def overlap_chunk(metin, chunk_boyutu=200, overlap=30):
    chunklar = []
    baslangic = 0

    while baslangic < len(metin):
        bitis = baslangic + chunk_boyutu

        chunklar.append(
            metin[baslangic:bitis]
        )

        baslangic += chunk_boyutu - overlap

    return chunklar


def paragraf_chunk(metin, max_boyut=500):
    paragraflar = metin.split("\n\n")

    chunklar = []
    mevcut_chunk = ""

    for paragraf in paragraflar:

        if len(mevcut_chunk) + len(paragraf) <= max_boyut:
            mevcut_chunk += paragraf + "\n\n"

        else:
            if mevcut_chunk:
                chunklar.append(mevcut_chunk.strip())

            mevcut_chunk = paragraf + "\n\n"

    if mevcut_chunk:
        chunklar.append(
            mevcut_chunk.strip()
        )

    return chunklar


metin = """Şirketimiz çalışanlarına yılda 14 gün yıllık izin verir.
İzin talepleri yöneticinin onayına sunulur.
Çalışanlar izin başvurularını şirketin insan kaynakları sistemi üzerinden yapabilir.

Uzaktan çalışanlar VPN kullanmalıdır.
Şirket bilgisayarları düzenli olarak güncellenir.
Çalışanların şirket sistemlerine bağlanırken güvenli bağlantı kullanması zorunludur.

Çalışanlara her ayın sonunda maaş ödemesi yapılır.
Maaş bilgileri çalışanlara özel tutulur.
Maaş bordroları çalışanların kişisel hesapları üzerinden görüntülenebilir.

Şirket çalışanlarının güvenlik eğitimlerine katılması zorunludur.
Yeni çalışanlara ilk hafta içerisinde şirket politikaları anlatılır.
Çalışanlar şirket kaynaklarını yalnızca iş amaçlı kullanmalıdır.

Yıllık performans değerlendirmeleri her yılın sonunda gerçekleştirilir.
Yöneticiler çalışanlarla performans görüşmeleri yapar.
Performans sonuçları çalışanların gelişim planlarında kullanılır."""



chunklar = sabit_boyutlu_chunk(
    metin,
    chunk_boyutu=200
)

for i, chunk in enumerate(chunklar):
    print(f"\nChunk {i}:")
    print(chunk)


chunklar = overlap_chunk(
    metin,
    chunk_boyutu=200,
    overlap=30
)

for i, chunk in enumerate(chunklar):
    print(f"\nChunk {i}:")
    print(chunk)



chunklar = paragraf_chunk(
    metin,
    max_boyut=200
)

for i, chunk in enumerate(chunklar):
    print(f"\nChunk {i}:")
    print(chunk)


chunklar = paragraf_chunk(
    metin,
    max_boyut=250
)

sonuc_chunk = vo.embed(
    chunklar,
    model="voyage-4",
    input_type="document"
)

chunk_embeddingleri = sonuc_chunk.embeddings


soru = "Yıllık izin kaç gün?"

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


sonuclar = []

for i, chunk_vektoru in enumerate(chunk_embeddingleri):

    skor = kosinus_benzerlik(
        soru_vektor,
        chunk_vektoru
    )

    sonuclar.append(
        (skor, chunklar[i])
    )


sonuclar.sort(reverse=True)


for skor, chunk in sonuclar:
    print(f"\nSkor: {skor:.4f}")
    print(chunk)


chunklar_100 = paragraf_chunk(
    metin,
    max_boyut=100
)

chunklar_1000 = paragraf_chunk(
    metin,
    max_boyut=1000
)

print(
    "100 karakterlik chunk sayısı:",
    len(chunklar_100)
)

print(
    "1000 karakterlik chunk sayısı:",
    len(chunklar_1000)
)