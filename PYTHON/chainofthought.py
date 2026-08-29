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
        "content": "İstanbul'da hava nasıl?"
    }
]


mesaj = client.messages.create(
    model=MODEL,
    max_tokens=500,
    tools=araclar,
    messages=mesajlar
)


tool_blogu = None

for blok in mesaj.content:
    if blok.type == "tool_use":
        tool_blogu = blok
        break


if tool_blogu:
    if tool_blogu.name == "hesap_makinesi":
        sonuc = hesap_makinesi_calistir(**tool_blogu.input)

    elif tool_blogu.name == "hava_durumu":
        sonuc = hava_durumu_calistir(**tool_blogu.input)

    mesajlar.append({
        "role": "assistant",
        "content": mesaj.content
    })

    mesajlar.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_blogu.id,
                "content": str(sonuc)
            }
        ]
    })

    son_mesaj = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=araclar,
        messages=mesajlar
    )

    print(son_mesaj.content[0].text)

else:
    print(mesaj.content[0].text)