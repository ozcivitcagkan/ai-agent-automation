import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"


def hesap_makinesi_calistir(islem, sayi1, sayi2):
    if islem == "topla":
        return sayi1 + sayi2
    elif islem == "cikar":
        return sayi1 - sayi2
    elif islem == "carp":
        return sayi1 * sayi2
    elif islem == "bol":
        return sayi1 / sayi2


def hava_durumu_calistir(sehir):
    dummy_veri = {
        "İstanbul": "22°C, parçalı bulutlu",
        "Ankara": "18°C, açık"
    }

    return dummy_veri.get(sehir, "Bu şehir için veri yok")


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
        "description": "Bir şehrin güncel hava durumunu verir.",
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


mesajlar = [
    {
        "role": "user",
        "content": "İstanbul'un sıcaklığını öğren ve sonra bu sıcaklığı 7 ile çarp."
    }
]


MAX_ADIM = 5
adim = 0


while adim < MAX_ADIM:

    adim += 1

    mesaj = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=araclar,
        messages=mesajlar
    )

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
        print(f"Girdi: {blok.input}")

        if blok.name == "hesap_makinesi":

            sonuc = hesap_makinesi_calistir(**blok.input)

        elif blok.name == "hava_durumu":

            sonuc = hava_durumu_calistir(**blok.input)

        else:

            sonuc = f"Bilinmeyen tool: {blok.name}"

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

    print(f"Agent MAX_ADIM sınırına ulaştı: {MAX_ADIM}")