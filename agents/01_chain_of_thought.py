import anthropic
import os
from dotenv import load_dotenv
import re
import json

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"

def sor(prompt):
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

    return mesaj.content[0].text


cevap = sor("Python nedir? Bir cümleyle açıkla.")

yorum = "Kargo çok geç geldi ama ürün gerçekten kaliteli, tekrar alırım."

prompt = f"""
Aşağıdaki ürün yorumunu analiz et.

Yorum: {yorum}

Sadece JSON döndür, başka hiçbir açıklama yazma.

{{
    "duygu": "pozitif/negatif/notr",
    "sikayet_var_mi": true,
    "ozet": "en fazla 5 kelime"
}}
"""

cevap = sor(prompt)

# sonuc = re.search(r"<duygu>(.*?)</duygu>", cevap)
# sonuc2 = re.search(r"<sikayet_var_mi>(.*?)</sikayet_var_mi>", cevap)
# sonuc3 = re.search(r"<ozet>(.*?)</ozet>", cevap)

# duygu = sonuc.group(1)
# sikayet = sonuc2.group(1)
# ozet = sonuc3.group(1)

# print(duygu)
# print(sikayet)
# print(ozet)

cevap = cevap.replace("```json", "")
cevap = cevap.replace("```", "")
cevap = cevap.strip()

veri = json.loads(cevap)

# print(type(veri))
# print(veri["duygu"])
# print(veri["sikayet_var_mi"])
# print(veri["ozet"])

yorumlar = [
    "Ürün harika, çok memnun kaldım.",
    "Kargo çok geç geldi ve ürün kırık çıktı.",
    "Fiyatına göre fena değil.",
    "Ürünü iki gündür kullanıyorum, şimdilik iyi görünüyor.",
    "Tam bir hayal kırıklığı, kesinlikle tavsiye etmiyorum."
]


for yorum in yorumlar:

    prompt = f"""
    Aşağıdaki ürün yorumunu analiz et.

    Yorum: {yorum}

    Sadece JSON döndür.

    {{
        "duygu": "pozitif",
        "sikayet_var_mi": true,
        "ozet": "en fazla 5 kelime"
    }}
    """

    try:
        veri = json.loads(cevap)
        print("JSON başarılı")
    except json.JSONDecodeError:
        print("JSON BOZULDU")



prompt1 = """
Bir mağazada 23 elma var.
17'si satıldı.
Sonra 8 kasa daha geldi.
Her kasada 12 elma var.
Şu an kaç elma var?
Sadece sonucu söyle.
"""

cevap1 = sor(prompt1)

# print("DİREK:")
# print(cevap1)

prompt2 = """
Bir mağazada 23 elma var.
17'si satıldı.
Sonra 8 kasa daha geldi.
Her kasada 12 elma var.

Hesabı kısa adımlara ayır ve en sonunda sonucu belirt.
"""

cevap2 = sor(prompt2)

# print("CHAIN OF THOUGHT LU HALİ:")
# print(cevap2)


mesajlar = [
    "İstanbul'un nüfusu kaç?",
    "125'in yüzde 18'i kaç?",
    "Bugün çok yoruldum."
]

for mesaj in mesajlar:

    prompt = f"""
    Kullanıcının mesajını analiz et.

    Kullanıcı: {mesaj}

    Kısa bir gerekçe ver ve hangi aracın
    kullanılması gerektiğine karar ver.

    <gerekce>kısa gerekçe</gerekce>
    <arac>bilgi, hesap_makinesi veya arac_yok</arac>
    """

    cevap = sor(prompt)

    print("\nuser:", mesaj)
    print(cevap)