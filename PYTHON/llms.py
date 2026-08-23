import os 
from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL = "claude-haiku-4-5"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def sor(soru, sistem =None, max_tokens = 300):
    parametreler = {
        "model" : MODEL,
        "max_tokens" : max_tokens,
        "messages" : [{"role": "user", "content" : soru}]
    }

    if sistem:
        parametreler["system"] = sistem

    mesaj = client.messages.create(**parametreler)

    if mesaj.stop_reason == "max_tokens":
        print("uyarı: cevap durdu, max token arttirilmali")

    print(mesaj.usage.input_tokens, mesaj.usage.output_tokens)

    return mesaj.content[0].text

print(sor("Tell me more about the world", max_tokens=20))
