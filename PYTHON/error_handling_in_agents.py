import anthropic
import time

from dotenv import load_dotenv
from anthropic import RateLimitError, APIError

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"


def hesap_makinesi_calistir(islem, sayi1, sayi2):

    try:

        if islem == "topla":
            return sayi1 + sayi2

        elif islem == "cikar":
            return sayi1 - sayi2

        elif islem == "carp":
            return sayi1 * sayi2

        elif islem == "bol":

            if sayi2 == 0:
                return "HATA: Sıfıra bölme yapılamaz"

            return sayi1 / sayi2

        else:
            return f"HATA: Bilinmeyen işlem: {islem}"

    except Exception as e:

        return f"HATA: Hesaplama sırasında hata oluştu: {str(e)}"


def hava_durumu_calistir(sehir=None):

    if not sehir:
        return "HATA: Şehir belirtilmedi"

    dummy_veri = {
        "İstanbul": "22°C, parçalı bulutlu",
        "Ankara": "18°C, açık"
    }

    if sehir not in dummy_veri:

        mevcut_sehirler = list(dummy_veri.keys())

        return (
            f"HATA: '{sehir}' için veri bulunamadı. "
            f"Mevcut şehirler: {mevcut_sehirler}"
        )

    return dummy_veri[sehir]

system_prompt = """
Tool bir hata döndürürse kullanıcıya kısa ve doğrudan cevap ver.
Ek açıklama, emoji veya gereksiz öneri ekleme.
"""

araclar = [

    {
        "name": "hesap_makinesi",

        "description": (
            "İki sayı arasında toplama, çıkarma, "
            "çarpma veya bölme işlemi yapar."
        ),

        "input_schema": {

            "type": "object",

            "properties": {

                "islem": {
                    "type": "string",
                    "enum": [
                        "topla",
                        "cikar",
                        "carp",
                        "bol"
                    ]
                },

                "sayi1": {
                    "type": "number"
                },

                "sayi2": {
                    "type": "number"
                }
            },

            "required": [
                "islem",
                "sayi1",
                "sayi2"
            ]
        }
    },

    {
        "name": "hava_durumu",
        "description": "Bir şehrin güncel hava durumunu verir.",
        "input_schema": {
            "type": "object",
            "properties": {

                "sehir": {
                    "type": "string"
                }
            },

            "required": [
                "sehir"
            ]
        }
    }
]



ARAC_FONKSIYONLARI = {

    "hesap_makinesi": hesap_makinesi_calistir,
    "hava_durumu": hava_durumu_calistir
}

def guvenli_istek(mesajlar, deneme=3):

    for i in range(deneme):

        try:

            return client.messages.create(
                model=MODEL,
                max_tokens=500,
                tools=araclar,
                system=system_prompt,
                messages=mesajlar
            )

        except RateLimitError:

            bekleme = 2 ** i

            print(
                f"Rate limit oluştu. "
                f"{bekleme} saniye bekleniyor..."
            )

            time.sleep(bekleme)

        except APIError as e:

            print(f"API hatası: {e}")

            raise

    raise Exception(
        "Maksimum API deneme sayısına ulaşıldı."
    )

# mesajlar = [

#     {
#         "role": "user",
#         "content": "Paris'te hava nasıl?"
#     }

# ]

mesajlar = [

    {
        "role": "user",
        "content": "10'u 0'a böl"
    }

]


MAX_ADIM = 5

adim = 0


while adim < MAX_ADIM:

    adim += 1
    mesaj = guvenli_istek(mesajlar)


    mesajlar.append({

        "role": "assistant",
        "content": mesaj.content

    })


    if mesaj.stop_reason != "tool_use":

        for blok in mesaj.content:
            if blok.type == "text":
                print(blok.text)

        break



    tool_sonuclari = []



    for blok in mesaj.content:
        if blok.type != "tool_use":
            continue


        print(f"Tool çağrıldı: {blok.name}")



        fonksiyon = ARAC_FONKSIYONLARI.get(
            blok.name
        )



        if fonksiyon is None:

            sonuc = (
                f"HATA: '{blok.name}' "
                f"adında bir araç yok"
            )


        else:

            try:

                sonuc = fonksiyon(**blok.input)

            except Exception as e:

                sonuc = (
                    "HATA: Araç çalışırken "
                    f"hata oluştu: {str(e)}"
                )


        print(f"Tool sonucu: {sonuc}")


        tool_sonuclari.append({

            "type": "tool_result",
            "tool_use_id": blok.id,
            "content": str(sonuc)

        })



    mesajlar.append({

        "role": "user",
        "content": tool_sonuclari

    })


if adim >= MAX_ADIM:

    print(
        "\nÜzgünüm, bu isteği tamamlayamadım. "
        "Çok fazla işlem gerekti."
    )