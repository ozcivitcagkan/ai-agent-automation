import os
import glob
import voyageai
import chromadb
import anthropic

from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document


load_dotenv()

MODEL = "claude-haiku-4-5"


client_db = chromadb.PersistentClient(path="./chroma_db")

koleksiyon = client_db.get_or_create_collection(
    name="gercek_dosyalar"
)

vo = voyageai.Client()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)



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
        chunklar.append(mevcut_chunk.strip())

    return chunklar



def txt_oku(dosya_yolu):
    with open(
        dosya_yolu,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()



def pdf_oku(dosya_yolu):
    reader = PdfReader(dosya_yolu)

    tum_metin = ""

    for sayfa in reader.pages:
        sayfa_metni = sayfa.extract_text() or ""
        tum_metin += sayfa_metni + "\n"

    return tum_metin




def docx_oku(dosya_yolu):
    dokuman = Document(dosya_yolu)

    tum_metin = ""

    for paragraf in dokuman.paragraphs:
        tum_metin += paragraf.text + "\n"

    return tum_metin


def dosya_oku(dosya_yolu):
    uzanti = os.path.splitext(dosya_yolu)[1].lower()

    if uzanti == ".txt":
        return txt_oku(dosya_yolu)

    elif uzanti == ".pdf":
        return pdf_oku(dosya_yolu)

    elif uzanti == ".docx":
        return docx_oku(dosya_yolu)

    else:
        raise ValueError(
            f"Desteklenmeyen dosya türü: {uzanti}"
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



def dosyayi_koleksiyona_ekle(
    dosya_yolu,
    koleksiyon_adi="gercek_dosyalar"
):
    metin = dosya_oku(dosya_yolu)

    chunklar = paragraf_chunk(
        metin,
        max_boyut=500
    )

    if not chunklar:
        print(f"Dosyada metin bulunamadı: {dosya_yolu}")
        return

    embeddingler = voyage_embed_document(
        chunklar
    )

    dosya_adi = os.path.basename(
        dosya_yolu
    )

    ids = [
        f"{dosya_adi}_{i}"
        for i in range(len(chunklar))
    ]

    metadatas = [
        {
            "kaynak": dosya_adi,
            "chunk_no": i
        }
        for i in range(len(chunklar))
    ]

    koleksiyon.add(
        ids=ids,
        embeddings=embeddingler,
        documents=chunklar,
        metadatas=metadatas
    )

    print(
        f"{len(chunklar)} chunk eklendi: {dosya_adi}"
    )



def klasordeki_tum_dosyalari_ekle(klasor_yolu):
    dosyalar = (
        glob.glob(
            os.path.join(klasor_yolu, "*.txt")
        )
        + glob.glob(
            os.path.join(klasor_yolu, "*.pdf")
        )
        + glob.glob(
            os.path.join(klasor_yolu, "*.docx")
        )
    )

    for dosya in dosyalar:
        dosyayi_koleksiyona_ekle(dosya)




def ilgili_chunklari_bul_detayli(
    soru,
    n=3
):
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
                "kaynak": sonuclar["metadatas"][0][i]["kaynak"],
                "chunk_no": sonuclar["metadatas"][0][i]["chunk_no"]
            }
        )

    return detayli



def rag_prompt_olustur(
    soru,
    chunklar
):
    baglam = "\n\n".join(
        [chunk["metin"] for chunk in chunklar]
    )

    kaynaklar = "\n".join(
        [
            f"- {chunk['kaynak']} / chunk {chunk['chunk_no']}"
            for chunk in chunklar
        ]
    )

    prompt = f"""Aşağıdaki bağlamı kullanarak soruyu cevapla.

Sadece bağlamdaki bilgiyi kullan.
Bağlamda cevap yoksa "Bu bilgi elimde yok" de.
Hiçbir şey uydurma.

Bağlam:
{baglam}

Soru:
{soru}

Kaynaklar:
{kaynaklar}

Cevap:
"""

    return prompt


def rag_sor(soru, n=3):
    chunklar = ilgili_chunklari_bul_detayli(
        soru,
        n=n
    )

    prompt = rag_prompt_olustur(
        soru,
        chunklar
    )

    mesaj = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    cevap = mesaj.content[0].text

    return cevap, chunklar



if __name__ == "__main__":

    dosya = "izin_politikasi.txt"

    print("\n===== GÖREV A: TXT =====")

    txt_metin = txt_oku(dosya)

    print(txt_metin)


    # =====================================================
    # 15. GÖREV B: PDF OKUMA
    # =====================================================

    print("\n===== GÖREV B: PDF =====")

    pdf_metin = pdf_oku(
        "izin_politikasi.pdf"
    )

    print(pdf_metin)


    # =====================================================
    # 16. GÖREV C: GENEL DOSYA OKUYUCU
    # =====================================================

    print("\n===== GÖREV C: GENEL OKUYUCU =====")

    print(
        "\nTXT uzunluğu:",
        len(
            dosya_oku(
                "izin_politikasi.txt"
            )
        )
    )

    print(
        "PDF uzunluğu:",
        len(
            dosya_oku(
                "izin_politikasi.pdf"
            )
        )
    )

    print(
        "DOCX uzunluğu:",
        len(
            dosya_oku(
                "izin_politikasi.docx"
            )
        )
    )


    # =====================================================
    # 17. GÖREV D: GERÇEK DOSYAYI CHROMA'YA EKLE
    # =====================================================

    print("\n===== GÖREV D: CHROMA =====")

    onceki_sayi = koleksiyon.count()

    print(
        "Önceki kayıt sayısı:",
        onceki_sayi
    )

    dosyayi_koleksiyona_ekle(
        "izin_politikasi.txt"
    )

    sonraki_sayi = koleksiyon.count()

    print(
        "Sonraki kayıt sayısı:",
        sonraki_sayi
    )


    # =====================================================
    # 18. GÖREV E: GERÇEK DOSYADAN SORU CEVAPLAMA
    # =====================================================

    print("\n===== GÖREV E: RAG =====")

    soru = "Yıllık izin kaç gün?"

    cevap, kaynaklar = rag_sor(
        soru,
        n=3
    )

    print("\nSoru:")
    print(soru)

    print("\nCevap:")
    print(cevap)

    print("\nKullanılan kaynaklar:")

    for kaynak in kaynaklar:
        print(
            f"- {kaynak['kaynak']} "
            f"/ chunk {kaynak['chunk_no']}"
        )


    # =====================================================
    # 19. GÖREV F: AYNI DOSYAYI TEKRAR EKLE
    # =====================================================

    print("\n===== GÖREV F: ID TESTİ =====")

    onceki_sayi = koleksiyon.count()

    print(
        "İlk count:",
        onceki_sayi
    )

    dosyayi_koleksiyona_ekle(
        "izin_politikasi.txt"
    )

    sonraki_sayi = koleksiyon.count()

    print(
        "İkinci count:",
        sonraki_sayi
    )

    if sonraki_sayi == onceki_sayi:
        print(
            "Aynı ID'ler nedeniyle yeni kayıt sayısı artmadı."
        )
    else:
        print(
            "Kayıt sayısı değişti. "
            "ID davranışını Chroma sonucuyla gözlemle."
        )
