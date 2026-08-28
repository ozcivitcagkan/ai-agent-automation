import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL = "claude-haiku-4-5"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def sor(soru, sistem=None, max_tokens=500):
    parametreler = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": soru}]
    }
    if sistem:
        parametreler["system"] = sistem

    mesaj = client.messages.create(**parametreler)
    return mesaj.content[0].text


soru = "Kod tekrarı neden kötüdür?"


# roller = [
#     "Sen yeni başlayanlara ders veren bir öğretmensin. En fazla 3 cümle yaz.",
#     "Sen kıdemli bir yazılım mimarısın. En fazla 3 cümle yaz.",
#     "Sen çok yoğun bir teknik lidersin. Tam olarak 3 madde yaz, her madde en fazla 8 kelime, başlık atma, kod yok."
# ]

# for rol in roller:
#     print(f"--- {rol} ---")
#     print(sor(soru, sistem=rol, max_tokens=150))
#     print()


zero_shot = """Sadece tek kelime cevap ver: pozitif, negatif veya nötr..

Yorum: Ürün fena değil"""

print(sor(zero_shot, max_tokens=100))

few_shot = """Yorumları sınıflandır. Sadece tek kelime cevap ver. Pozitif, negatif veya nötr.

Yorum: Harika bir ürün, çok memnunum
Sınıf: pozitif

Yorum: Kötü ürün
Sınıf: negatif

Yorum: Fena değil
Sınıf: nötr

Yorum: Ürün fena değil

cevabı yaz direk.
"""


print(sor(few_shot, max_tokens=20))