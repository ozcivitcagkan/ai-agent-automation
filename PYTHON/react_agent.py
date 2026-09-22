import anthropic
import os
from dotenv import load_dotenv


load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

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


ARAC_FONKSIYONLARI = {
    "hesap_makinesi": hesap_makinesi_calistir,
    "hava_durumu": hava_durumu_calistir
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
    }
]


react_system_prompt = """Sen bir görevi adım adım çözen bir asistansın.

Her adımda önce ne yapman gerektiğini KISACA açıkla,
sonra gerekiyorsa aracı çağır.

Düşüncelerini bir cümleyle sınırla.
Yeterli bilgiye ulaştığında nihai cevabını ver.
"""


def react_agent_calistir(soru, max_adim=5):
    mesajlar = [
        {
            "role": "user",
            "content": soru
        }
    ]

    adim = 0

    while adim < max_adim:
        adim += 1

        mesaj = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=react_system_prompt,
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
                print(
                    f"[Adım {adim} - Düşünce/Cevap]: "
                    f"{blok.text}"
                )

        if mesaj.stop_reason != "tool_use":
            break

        tool_sonuclari = []

        for blok in mesaj.content:
            if blok.type != "tool_use":
                continue

            fonksiyon = ARAC_FONKSIYONLARI.get(blok.name)

            print(
                f"[Adım {adim} - Eylem]: "
                f"{blok.name}({blok.input})"
            )

            if fonksiyon is None:
                sonuc = f"HATA: '{blok.name}' adında bir araç yok"

            else:
                try:
                    sonuc = fonksiyon(**blok.input)

                except Exception as e:
                    sonuc = f"HATA: {str(e)}"

            print(
                f"[Adım {adim} - Gözlem]: {sonuc}"
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

    if adim >= max_adim:
        print("\n⚠️ Maksimum adım sayısına ulaşıldı.")


if __name__ == "__main__":
    react_agent_calistir(
        "Ankara'da hava nasıl, ve eğer sıcaklık 20'den düşükse bunu 3 ile çarp, değilse 5 ile çarp."
    )