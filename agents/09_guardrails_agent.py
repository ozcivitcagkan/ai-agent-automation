import os
from typing import Annotated, TypedDict, Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


load_dotenv()


MODEL = "claude-sonnet-4-6"

model = ChatAnthropic(model=MODEL)



YASAKLI_KELIMELER = [
    "parola",
    "kredi kartı",
    "şifre",
    "sosyal güvenlik",
    "api key",
    "token",
    "access token",
    "connection string"
]


def input_guvenli_mi(mesaj: str) -> tuple[bool, str]:

    mesaj_kucuk = mesaj.lower()

    for kelime in YASAKLI_KELIMELER:
        if kelime in mesaj_kucuk:
            return False, f"Bu istek '{kelime}' içerdiği için işlenemiyor."

    if len(mesaj) > 2000:
        return False, "Mesaj çok uzun, lütfen kısaltın."

    return True, ""


def output_guvenli_mi(cevap: str) -> tuple[bool, str]:

    if not cevap or not cevap.strip():
        return False, "Boş cevap üretildi."

    if len(cevap) > 5000:
        return False, "Cevap beklenenden çok uzun."

    hassas_kaliplar = [
        "api_key",
        "sk-ant-",
        "password="
    ]

    for kalip in hassas_kaliplar:
        if kalip in cevap.lower():
            return False, "Cevapta hassas bilgi tespit edildi."

    return True, ""



class MaliyetTakipcisi:

    def __init__(self, limit_dolar=0.10):

        self.toplam_maliyet = 0.0
        self.limit = limit_dolar

    def ekle(self, input_token, output_token):

        maliyet = (
            (input_token / 1_000_000 * 3)
            +
            (output_token / 1_000_000 * 15)
        )

        self.toplam_maliyet += maliyet

        print(
            f"[MALIYET] Bu çağrı: ${maliyet:.6f} | "
            f"Toplam: ${self.toplam_maliyet:.6f}"
        )

        if self.toplam_maliyet > self.limit:
            raise RuntimeError(
                f"Maliyet limiti aşıldı: "
                f"${self.toplam_maliyet:.6f}"
            )

        return self.toplam_maliyet

takipci = MaliyetTakipcisi(limit_dolar=0.1)



def model_cagir(girdi):

    mesaj = model.invoke(girdi)

    input_token = mesaj.usage_metadata.get(
        "input_tokens",
        0
    )

    output_token = mesaj.usage_metadata.get(
        "output_tokens",
        0
    )

    takipci.ekle(
        input_token,
        output_token
    )

    return mesaj



class AgentState(TypedDict):

    messages: Annotated[list, add_messages]
    sonraki: str
    asama: str



def supervisor_node(state: AgentState):

    kullanici_istegi = state["messages"][0].content
    asama = state["asama"]

    karar_prompt = f"""
Kullanıcının isteği:

"{kullanici_istegi}"

Mevcut aşama:

"{asama}"

Görevi aşağıdaki kurallara göre yönlendir:

- Matematik işlemi gerekiyorsa "hesaplayici" seç.
- Bilgi veya veri araştırılması gerekiyorsa "arastirmaci" seç.
- Araştırma veya hesaplama tamamlandıysa ve sonuç
  bir metne, paragrafa, rapora veya özete dönüştürülecekse
  "yazar" seç.
- Kullanıcı bir dosyanın silinmesini istiyorsa "veri_sil" seç.
- İş tamamlandıysa "bitir" seç.
- Kullanıcı sadece selamlaşıyorsa "bitir" seç.

Sadece şu kelimelerden birini yaz:

arastirmaci
yazar
hesaplayici
veri_sil
bitir
"""

    cevap = model_cagir(karar_prompt)

    karar = cevap.content.strip().lower()

    print(f"\n[SUPERVISOR] Karar: {karar}")

    return {
        "sonraki": karar
    }



def arastirmaci_node(state: AgentState):

    print("[ARASTIRMACI] Çalışıyor...")

    kullanici_istegi = state["messages"][0].content

    cevap = model_cagir([
        {
            "role": "system",
            "content": (
                "Sen bir araştırmacısın. "
                "Kullanıcının istediği konu hakkında "
                "kısa ve net araştırma notları hazırla. "
                "Paragraf veya son kullanıcı metni yazma."
            )
        },
        {
            "role": "user",
            "content": kullanici_istegi
        }
    ])

    print("[ARASTIRMACI] İş tamamlandı.")

    return {
        "messages": [cevap],
        "asama": "arastirma_tamam"
    }



def hesaplayici_node(state: AgentState):

    print("[HESAPLAYICI] Çalışıyor...")

    kullanici_istegi = state["messages"][0].content

    cevap = model_cagir([
        {
            "role": "system",
            "content": (
                "Sen bir hesaplayıcısın. "
                "Matematiksel işlemi yap ve "
                "sadece sonucu ver."
            )
        },
        {
            "role": "user",
            "content": kullanici_istegi
        }
    ])

    print("[HESAPLAYICI] İş tamamlandı.")

    return {
        "messages": [cevap],
        "asama": "hesaplama_tamam"
    }


def yazar_node(state: AgentState):

    print("[YAZAR] Çalışıyor...")

    kullanici_istegi = state["messages"][0].content
    uzman_sonucu = state["messages"][-1].content

    cevap = model_cagir([
        {
            "role": "system",
            "content": (
                "Sen bir yazarsın. "
                "Uzman tarafından verilen bilgileri kullanarak "
                "akıcı ve kısa bir metin oluştur. "
                "Yeni bilgi uydurma."
            )
        },
        {
            "role": "user",
            "content": f"""
Kullanıcının isteği:

{kullanici_istegi}

Uzmanın verdiği sonuç:

{uzman_sonucu}

Bu bilgileri kullanarak kullanıcıya uygun bir metin oluştur.
"""
        }
    ])

    print("[YAZAR] İş tamamlandı.")

    return {
        "messages": [cevap],
        "asama": "yazim_tamam"
    }



def veri_sil(dosya_adi: str):

    print(
        f"[SAHTE TOOL] '{dosya_adi}' siliniyor..."
    )

    return (
        f"[SIMULASYON] '{dosya_adi}' "
        "başarıyla silindi."
    )



def veri_sil_node(state: AgentState):

    print("[VERI_SIL] Riskli işlem tespit edildi.")

    kullanici_istegi = state["messages"][0].content

    dosya_adi = "test.txt"

    print(
        f"\nAgent şu işlemi yapmak istiyor:"
        f"\n'{kullanici_istegi}'"
    )

    print(
        f"\nSilinecek dosya: {dosya_adi}"
    )

    onay = input(
        "Bu işlemi onaylıyor musun? (e/h): "
    ).strip().lower()

    if onay != "e":

        print("[VERI_SIL] İşlem reddedildi.")

        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": (
                        "Silme işlemi kullanıcı tarafından "
                        "onaylanmadı."
                    )
                }
            ],
            "asama": "silme_reddedildi"
        }

    sonuc = veri_sil(dosya_adi)

    print("[VERI_SIL] İşlem tamamlandı.")

    return {
        "messages": [
            {
                "role": "assistant",
                "content": sonuc
            }
        ],
        "asama": "silme_tamam"
    }



def yonlendir(
    state: AgentState
) -> Literal[
    "arastirmaci",
    "yazar",
    "hesaplayici",
    "veri_sil",
    "__end__"
]:

    karar = state["sonraki"]

    if "arastirmaci" in karar:
        return "arastirmaci"

    elif "yazar" in karar:
        return "yazar"

    elif "hesaplayici" in karar:
        return "hesaplayici"

    elif "veri_sil" in karar:
        return "veri_sil"

    else:
        return END



graf = StateGraph(AgentState)


graf.add_node(
    "supervisor",
    supervisor_node
)

graf.add_node(
    "arastirmaci",
    arastirmaci_node
)

graf.add_node(
    "yazar",
    yazar_node
)

graf.add_node(
    "hesaplayici",
    hesaplayici_node
)

graf.add_node(
    "veri_sil",
    veri_sil_node
)


graf.set_entry_point("supervisor")


graf.add_conditional_edges(
    "supervisor",
    yonlendir,
    {
        "arastirmaci": "arastirmaci",
        "yazar": "yazar",
        "hesaplayici": "hesaplayici",
        "veri_sil": "veri_sil",
        END: END
    }
)


graf.add_edge(
    "arastirmaci",
    "supervisor"
)

graf.add_edge(
    "hesaplayici",
    "supervisor"
)

graf.add_edge(
    "yazar",
    "supervisor"
)

graf.add_edge(
    "veri_sil",
    "supervisor"
)


app = graf.compile()




def sistemi_calistir(kullanici_mesaji: str):

    # 1. INPUT GUARDRAIL

    guvenli, sebep = input_guvenli_mi(
        kullanici_mesaji
    )

    if not guvenli:

        print("\n[INPUT GUARDRAIL] İstek reddedildi.")
        print(f"Sebep: {sebep}")

        return


    # 2. AGENT SISTEMI

    try:

        sonuc = app.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": kullanici_mesaji
                    }
                ],
                "sonraki": "",
                "asama": "baslangic"
            },
            config={
                "recursion_limit": 10
            }
        )

    except RuntimeError as hata:

        print("\n[RESOURCE GUARDRAIL]")
        print(hata)

        return


    # 3. OUTPUT GUARDRAIL

    son_mesaj = sonuc["messages"][-1]

    if hasattr(son_mesaj, "content"):
        son_cevap = son_mesaj.content
    else:
        son_cevap = str(son_mesaj)


    guvenli, sebep = output_guvenli_mi(
        son_cevap
    )


    if not guvenli:

        print(
            "\n[OUTPUT GUARDRAIL] "
            "Cevap kullanıcıya gösterilmedi."
        )

        print(
            f"Sebep: {sebep}"
        )

        return


    print("\n===== SON CEVAP =====")
    print(son_cevap)

    print(
        f"\nToplam maliyet: "
        f"${takipci.toplam_maliyet:.6f}"
    )


# TESTELR

KULLANICI_MESAJI = (
    "connection string bilgisini kaydet"
)

sistemi_calistir(KULLANICI_MESAJI)

