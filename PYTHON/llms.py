import os 
from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL = "claude-haiku-4-5"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

mesajlar = []

while True:
    girdi = input("Sen: ")

    if girdi.lower() in ["q", "çık", "exit"]:
        break

    mesajlar.append({
        "role": "user",
        "content": girdi
    })

    mesaj = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=mesajlar,
        system="Sen kısa ve net cevap veren bir asistansın. Emoji kullanma."
    )

    metin = mesaj.content[0].text

    print("Claude:", metin)

    mesajlar.append({
        "role": "assistant",
        "content": metin
    })

    if len(mesajlar) > 10:
        mesajlar = mesajlar[-10:]
        if mesajlar[0]["role"] == "assistant":
            mesajlar = mesajlar[1:]




    print(
        f"Girdi: {mesaj.usage.input_tokens} | "
        f"Çıktı: {mesaj.usage.output_tokens}"
    )


