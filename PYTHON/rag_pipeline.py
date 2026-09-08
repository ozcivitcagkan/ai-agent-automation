import os
import numpy as np
import voyageai
import chromadb
import anthropic

from dotenv import load_dotenv


load_dotenv()

MODEL = "claude-haiku-4-5"

vo = voyageai.Client()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

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


def kosinus_benzerlik(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def ilgili_chunklari_bul(soru, n=3):

    soru_vektor = voyage_embed_query(soru)

    sonuclar = koleksiyon.query(
        query_embeddings=[soru_vektor],
        n_results=n
    )

    return sonuclar["documents"][0]


def rag_prompt_olustur(soru, chunklar):

    baglam = "\n\n".join(chunklar)

    prompt = f"""Aşağıdaki bağlamı kullanarak soruyu cevapla.

Sadece bağlamdaki bilgiyi kullan.
Bağlamda cevap yoksa "Bu bilgi elimde yok" de.
Hiçbir şey uydurma.
Kullanıcı yanlış bir varsayım yapıyorsa, bağlamdaki doğru bilgiyle düzelt.

Bağlam:
{baglam}

Soru:
{soru}

Cevap:
"""

    return prompt



def rag_sor(soru, n=3):

    chunklar = ilgili_chunklari_bul(
        soru,
        n
    )

    prompt = rag_prompt_olustur(
        soru,
        chunklar
    )

    mesaj = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    cevap = mesaj.content[0].text

    return cevap, chunklar


# soru = "Maaş ne zaman ödenir?"

# chunklar = ilgili_chunklari_bul(
#     soru,
#     n=3
# )

# print("\nSoru:", soru)

# for i, chunk in enumerate(chunklar):
#     print(f"\nChunk {i}:")
#     print(chunk)



# soru = "Yıllık izin kaç gün?"

# chunklar = ilgili_chunklari_bul(
#     soru,
#     n=3
# )

# prompt = rag_prompt_olustur(
#     soru,
#     chunklar
# )

# print("\nClaude a gönderilecek prompterk:")
# print(prompt)


sorular = [
    "Yıllık izin kaç gün?",
    "Maaş ne zaman ödenir?",
    "Uzaktan çalışanlar için kural nedir?"
]

for soru in sorular:

    cevap, kullanilan_chunklar = rag_sor(
        soru,
        n=3
    )

    print("\n--------------------------------")
    print("SORU:", soru)
    print("--------------------------------")

    print("\nCEVAP:")
    print(cevap)

    print("\nKULLANILAN CHUNKLAR:")

    for chunk in kullanilan_chunklar:
        print("-", chunk)


# soru = "Şirketin CEO'su kim?"

# cevap, kullanilan_chunklar = rag_sor(
#     soru,
#     n=3
# )

# print("\nSORU:")
# print(soru)

# print("\nCEVAP:")
# print(cevap)

# soru = "Yıllık izin 30 gün mü?"

# cevap, kullanilan_chunklar = rag_sor(
#     soru,
#     n=3
# )

# print("\nSORU:")
# print(soru)

# print("\nCEVAP:")
# print(cevap)


def ilgili_chunklari_bul_detayli(soru, n=3):

    soru_vektor = voyage_embed_query(
        soru
    )

    sonuclar = koleksiyon.query(
        query_embeddings=[soru_vektor],
        n_results=n
    )

    detayli = []

    for i, dokuman in enumerate(
        sonuclar["documents"][0]
    ):

        detayli.append(
            {
                "metin": dokuman,
                "kategori": sonuclar["metadatas"][0][i]["kategori"]
            }
        )

    return detayli


# soru = "Yıllık izin kaç gün?"

# detayli_sonuclar = ilgili_chunklari_bul_detayli(
#     soru,
#     n=3
# )

# print("\nSoru:", soru)

# for sonuc in detayli_sonuclar:

#     print("\nMetin:")
#     print(sonuc["metin"])

#     print("Kategori:")
#     print(sonuc["kategori"])

#  Son iki prompt rpm sınırına takıldı, daha sonra bakılacak.