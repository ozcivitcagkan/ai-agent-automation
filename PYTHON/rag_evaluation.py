import os
import voyageai
import chromadb
import anthropic

from dotenv import load_dotenv


load_dotenv()

MODEL = "claude-haiku-4-5"


RUN_TASK_A = False
RUN_TASK_B = False
RUN_TASK_C = False
RUN_TASK_D = False
RUN_TASK_E = True


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


def voyage_embed_query(metin):
    sonuc = vo.embed(
        [metin],
        model="voyage-4",
        input_type="query"
    )

    return sonuc.embeddings[0]



def ilgili_chunklari_bul_detayli(soru, n=3):

    soru_vektor = voyage_embed_query(soru)

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


test_sorulari = [
    {
        "soru": "Yıllık izin kaç gün?",
        "beklenen_kategori": "izin"
    },
    {
        "soru": "Maaş ne zaman ödenir?",
        "beklenen_kategori": "maas"
    },
    {
        "soru": "VPN kullanmak zorunlu mu?",
        "beklenen_kategori": "vpn"
    },
    {
        "soru": "Performans değerlendirmesi ne zaman yapılır?",
        "beklenen_kategori": "performans"
    },
    {
        "soru": "Çalışanların güvenlik eğitimi zorunlu mu?",
        "beklenen_kategori": "guvenlik"
    }
]


if RUN_TASK_A:

    dogru_sayisi = 0

    for test in test_sorulari:

        detayli = ilgili_chunklari_bul_detayli(
            test["soru"],
            n=1
        )

        bulunan_kategori = detayli[0]["kategori"]

        dogru_mu = (
            bulunan_kategori
            == test["beklenen_kategori"]
        )

        if dogru_mu:
            dogru_sayisi += 1

        print(
            f"{'✅' if dogru_mu else '❌'} "
            f"{test['soru']}"
        )

        print(
            f"   Beklenen: {test['beklenen_kategori']} "
            f"| Bulunan: {bulunan_kategori}"
        )

    print(
        f"\nDoğruluk: "
        f"{dogru_sayisi}/{len(test_sorulari)}"
    )

    print(
        f"Oran: "
        f"{dogru_sayisi / len(test_sorulari) * 100:.1f}%"
    )




if RUN_TASK_B:

    for k in [1, 2, 3]:

        dogru_sayisi = 0

        for test in test_sorulari:

            detayli = ilgili_chunklari_bul_detayli(
                test["soru"],
                n=k
            )

            kategoriler = [
                d["kategori"]
                for d in detayli
            ]

            dogru_mu = (
                test["beklenen_kategori"]
                in kategoriler
            )

            if dogru_mu:
                dogru_sayisi += 1

        oran = (
            dogru_sayisi
            / len(test_sorulari)
            * 100
        )

        print(
            f"precision@{k}: "
            f"{dogru_sayisi}/{len(test_sorulari)} "
            f"({oran:.1f}%)"
        )



def rag_prompt_olustur(soru, chunklar):

    baglam = "\n\n".join(chunklar)

    prompt = f"""Aşağıdaki bağlamı kullanarak soruyu cevapla.

Sadece bağlamdaki bilgiyi kullan.
Bağlamda cevap yoksa "Bu bilgi elimde yok" de.
Hiçbir şey uydurma.
Kullanıcı yanlış bir varsayım yapıyorsa,
bağlamdaki doğru bilgiyle düzelt.

Bağlam:
{baglam}

Soru:
{soru}

Cevap:
"""

    return prompt



def generation_testi(
    soru,
    dogru_chunk,
    beklenen_anahtar_kelime
):

    prompt = rag_prompt_olustur(
        soru,
        [dogru_chunk]
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

    basarili = (
        beklenen_anahtar_kelime.lower()
        in cevap.lower()
    )

    print(
        f"{'✅' if basarili else '❌'} "
        f"{soru}"
    )

    print(
        f"   Cevap: {cevap}"
    )

    return basarili


if RUN_TASK_C:


    generation_testi(
        soru="Yıllık izin kaç gün?",
        dogru_chunk=(
            "Şirketimiz çalışanlarına "
            "yılda 14 gün yıllık izin verir."
        ),
        beklenen_anahtar_kelime="14"
    )

    generation_testi(
        soru="Maaş ne zaman ödenir?",
        dogru_chunk=(
            "Çalışanlara her ayın sonunda "
            "maaş ödemesi yapılır."
        ),
        beklenen_anahtar_kelime="ay"
    )

    generation_testi(
        soru="Uzaktan çalışanlar için kural nedir?",
        dogru_chunk=(
            "Uzaktan çalışanlar VPN "
            "kullanmalıdır."
        ),
        beklenen_anahtar_kelime="VPN"
    )


def rag_sor(soru, n=3):

    detayli = ilgili_chunklari_bul_detayli(
        soru,
        n=n
    )

    chunklar = [
        d["metin"]
        for d in detayli
    ]

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



if RUN_TASK_D:


    uctan_uca_testleri = [
        {
            "soru": "Yıllık izin kaç gün?",
            "beklenen": "14"
        },
        {
            "soru": "Maaş ne zaman ödenir?",
            "beklenen": "ay"
        },
        {
            "soru": "Uzaktan çalışanlar için kural nedir?",
            "beklenen": "VPN"
        },
        {
            "soru": "Şirketin CEO'su kim?",
            "beklenen": "elimde yok"
        },
        {
            "soru": "Yıllık izin 30 gün mü?",
            "beklenen": "14"
        }
    ]

    basarili_sayisi = 0

    for test in uctan_uca_testleri:

        cevap, chunklar = rag_sor(
            test["soru"],
            n=3
        )

        basarili = (
            test["beklenen"].lower()
            in cevap.lower()
        )

        if basarili:
            basarili_sayisi += 1

        print(
            f"\n{'✅' if basarili else '❌'} "
            f"{test['soru']}"
        )

        print(
            f"Cevap: {cevap}"
        )

    oran = (
        basarili_sayisi
        / len(uctan_uca_testleri)
        * 100
    )

    print(
        f"\nToplam başarı: "
        f"{basarili_sayisi}/"
        f"{len(uctan_uca_testleri)}"
    )

    print(
        f"Başarı oranı: {oran:.1f}%"
    )




def paragraf_chunk(metin, max_boyut=500):

    paragraflar = metin.split("\n\n")

    chunklar = []
    mevcut_chunk = ""

    for paragraf in paragraflar:

        if (
            len(mevcut_chunk)
            + len(paragraf)
            <= max_boyut
        ):

            mevcut_chunk += (
                paragraf + "\n\n"
            )

        else:

            if mevcut_chunk:
                chunklar.append(
                    mevcut_chunk.strip()
                )

            mevcut_chunk = (
                paragraf + "\n\n"
            )

    if mevcut_chunk:
        chunklar.append(
            mevcut_chunk.strip()
        )

    return chunklar



if RUN_TASK_E:
    

    metin = """Şirketimiz çalışanlarına yılda 14 gün yıllık izin verir.
İzin talepleri yöneticinin onayına sunulur.

Uzaktan çalışanlar VPN kullanmalıdır.
Şirket bilgisayarları düzenli olarak güncellenir.

Çalışanlara her ayın sonunda maaş ödemesi yapılır.
Maaş bilgileri çalışanlara özel tutulur.

Şirket çalışanlarının güvenlik eğitimlerine katılması zorunludur.
Yeni çalışanlara ilk hafta içerisinde şirket politikaları anlatılır.

Yıllık performans değerlendirmeleri her yılın sonunda gerçekleştirilir.
Yöneticiler çalışanlarla performans görüşmeleri yapar."""

    kucuk_chunklar = paragraf_chunk(
        metin,
        max_boyut=50
    )

    print(
        "\nOluşan chunk sayısı:",
        len(kucuk_chunklar)
    )

    for i, chunk in enumerate(
        kucuk_chunklar
    ):

        print(f"\nChunk {i}:")
        print(chunk)