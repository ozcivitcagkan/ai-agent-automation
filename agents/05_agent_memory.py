import anthropic
import os
import json
from dotenv import load_dotenv


load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

MODEL = "claude-sonnet-4-6"

HAFIZA_DOSYASI = "agent_hafiza.json"


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

    except Exception as e:
        return f"HATA: {str(e)}"


def hava_durumu_calistir(sehir=None):
    if not sehir:
        return "HATA: Şehir belirtilmedi"

    dummy_veri = {
        "İstanbul": "22°C, parçalı bulutlu",
        "Ankara": "18°C, açık"
    }

    return dummy_veri.get(
        sehir,
        f"HATA: '{sehir}' için veri yok. "
        f"Mevcut: {list(dummy_veri.keys())}"
    )


def hafizayi_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def hafizayi_kaydet(hafiza):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as file:
        json.dump(
            hafiza,
            file,
            ensure_ascii=False,
            indent=2
        )


def hafizaya_kaydet_calistir(anahtar, deger):
    hafiza = hafizayi_yukle()

    hafiza[anahtar] = deger

    hafizayi_kaydet(hafiza)

    return f"Kaydedildi: {anahtar} = {deger}"


def hafizadan_oku_calistir(anahtar):
    hafiza = hafizayi_yukle()

    return hafiza.get(
        anahtar,
        f"'{anahtar}' için kayıtlı bir bilgi yok"
    )


ARAC_FONKSIYONLARI = {
    "hesap_makinesi": hesap_makinesi_calistir,
    "hava_durumu": hava_durumu_calistir,
    "hafizaya_kaydet": hafizaya_kaydet_calistir,
    "hafizadan_oku": hafizadan_oku_calistir
}


araclar = [
    {
        "name": "hesap_makinesi",
        "description": "İki sayı arasında toplama, çıkarma, çarpma veya bölme işlemi yapar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "islem": {
                    "type": "string",
                    "enum": ["topla", "cikar", "carp", "bol"]
                },
                "sayi1": {
                    "type": "number"
                },
                "sayi2": {
                    "type": "number"
                }
            },
            "required": ["islem", "sayi1", "sayi2"]
        }
    },
    {
        "name": "hava_durumu",
        "description": "Bir şehrin hava durumunu verir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sehir": {
                    "type": "string"
                }
            },
            "required": ["sehir"]
        }
    },
    {
        "name": "hafizaya_kaydet",
        "description": "Kullanıcı hakkında ileride hatırlanması gereken kalıcı bir bilgiyi kaydeder. Örneğin isim veya tercih.",
        "input_schema": {
            "type": "object",
            "properties": {
                "anahtar": {
                    "type": "string",
                    "description": "Bilginin kısa adı. Örneğin isim."
                },
                "deger": {
                    "type": "string",
                    "description": "Kaydedilecek bilgi."
                }
            },
            "required": ["anahtar", "deger"]
        }
    },
    {
        "name": "hafizadan_oku",
        "description": "Daha önce kalıcı hafızaya kaydedilmiş bir bilgiyi okur.",
        "input_schema": {
            "type": "object",
            "properties": {
                "anahtar": {
                    "type": "string"
                }
            },
            "required": ["anahtar"]
        }
    }
]


def react_system_prompt_olustur():
    hafiza = hafizayi_yukle()

    hafiza_metni = ""

    if hafiza:
        hafiza_metni = "\n\nKullanıcı hakkında bildiklerin:\n"

        for anahtar, deger in hafiza.items():
            hafiza_metni += f"- {anahtar}: {deger}\n"

    return f"""Sen bir görevi adım adım çözen bir asistansın.

Her adımda önce ne yapman gerektiğini kısaca açıkla,
sonra gerekiyorsa aracı çağır.

Düşüncelerini bir cümleyle sınırla.

Kullanıcı kendisi hakkında kalıcı bir bilgi verirse
(hatırlanması gereken isim veya tercih gibi),
hafizaya_kaydet aracını kullan.

Gerektiğinde daha önce kaydedilmiş bilgileri
hafizadan_oku aracıyla kontrol et.

Yeterli bilgiye ulaştığında nihai cevabını ver.
{hafiza_metni}"""


def react_agent_baslat():
    mesajlar = []

    print("Agent hazır. Çıkmak için 'q' yaz.\n")

    while True:
        soru = input("Sen: ").strip()

        if soru.lower() in ["q", "çık", "exit"]:
            print("Görüşürüz!")
            break

        if not soru:
            continue

        mesajlar.append(
            {
                "role": "user",
                "content": soru
            }
        )

        adim = 0

        while adim < 5:
            adim += 1

            mesaj = client.messages.create(
                model=MODEL,
                max_tokens=500,
                system=react_system_prompt_olustur(),
                tools=araclar,
                messages=mesajlar
            )

            mesajlar.append(
                {
                    "role": "assistant",
                    "content": mesaj.content
                }
            )

            for blok in mesaj.content:
                if blok.type == "text" and blok.text.strip():
                    print(f"[Adım {adim}]: {blok.text}")

            if mesaj.stop_reason != "tool_use":
                break

            tool_sonuclari = []

            for blok in mesaj.content:
                if blok.type != "tool_use":
                    continue

                fonksiyon = ARAC_FONKSIYONLARI.get(blok.name)

                if fonksiyon is None:
                    sonuc = f"HATA: '{blok.name}' yok"

                else:
                    try:
                        sonuc = fonksiyon(**blok.input)

                    except Exception as e:
                        sonuc = f"HATA: {str(e)}"

                print(
                    f"[Eylem]: {blok.name}({blok.input}) → {sonuc}"
                )

                tool_sonuclari.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": blok.id,
                        "content": str(sonuc)
                    }
                )

            mesajlar.append(
                {
                    "role": "user",
                    "content": tool_sonuclari
                }
            )

        print()


if __name__ == "__main__":
    react_agent_baslat()