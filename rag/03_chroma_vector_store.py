import numpy as np
import voyageai
import chromadb
from dotenv import load_dotenv


load_dotenv()

vo = voyageai.Client()

client_db = chromadb.PersistentClient(
    path="./chroma_db"
)

koleksiyon = client_db.get_or_create_collection(
    name="sirket_politikalari"
)


def voyage_embed_document(metinler):
    sonuc = vo.embed(
        metinler,
        model="voyage-4",
        input_type="document"
    )

    return sonuc.embeddings


def voyage_embed_query(metin):
    sonuc = vo.embed(
        [metin],
        model="voyage-4",
        input_type="query"
    )

    return sonuc.embeddings[0]



chunklar = [
    "Şirketimiz çalışanlarına yılda 14 gün yıllık izin verir.",
    "Uzaktan çalışanlar VPN kullanmalıdır.",
    "Çalışanlara her ayın sonunda maaş ödemesi yapılır.",
    "Şirket çalışanlarının güvenlik eğitimlerine katılması zorunludur.",
    "Yıllık performans değerlendirmeleri her yılın sonunda gerçekleştirilir."
]


embeddingler = voyage_embed_document(
    chunklar
)

koleksiyon.add(
    ids=[
        "chunk_0",
        "chunk_1",
        "chunk_2",
        "chunk_3",
        "chunk_4"
    ],

    embeddings=embeddingler,

    documents=chunklar,

    metadatas=[
        {
            "kaynak": "sirket_politikalari.txt",
            "chunk_no": 0,
            "kategori": "izin"
        },
        {
            "kaynak": "sirket_politikalari.txt",
            "chunk_no": 1,
            "kategori": "vpn"
        },
        {
            "kaynak": "sirket_politikalari.txt",
            "chunk_no": 2,
            "kategori": "maas"
        },
        {
            "kaynak": "sirket_politikalari.txt",
            "chunk_no": 3,
            "kategori": "guvenlik"
        },
        {
            "kaynak": "sirket_politikalari.txt",
            "chunk_no": 4,
            "kategori": "performans"
        }
    ]
)


print(koleksiyon.count())


soru = "Yıllık izin kaç gün?"


soru_vektor = voyage_embed_query(
    soru
)


sonuclar = koleksiyon.query(
    query_embeddings=[soru_vektor],
    n_results=3
)


print(sonuclar["documents"])

print(sonuclar["distances"])

print(sonuclar["metadatas"])



filtreli_sonuclar = koleksiyon.query(
    query_embeddings=[soru_vektor],
    n_results=3,
    where={
        "kategori": "izin"
    }
)


print(
    filtreli_sonuclar["documents"]
)

# koleksiyon.delete(
#     ids=["chunk_1"]
# )



# koleksiyon.update(
#     ids=["chunk_0"],
#     documents=[
#         "Şirketimiz çalışanlarına yılda 20 gün yıllık izin verir."
#     ]
# )