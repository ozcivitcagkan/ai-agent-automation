from typing import Annotated, TypedDict, Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


load_dotenv()

MODEL = "claude-sonnet-4-6"

model = ChatAnthropic(model=MODEL)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    sonraki: str
    asama: str


def supervisor_node(state: AgentState):
    son_mesaj = state["messages"][-1].content
    asama = state["asama"]

    karar_prompt = f"""
Kullanıcının isteği:

"{state["messages"][0].content}"

Mevcut aşama:
"{asama}"

Kurallar:

- Eğer kullanıcı sadece basit bir selamlaşma yaptıysa "bitir" seç.
- Eğer kullanıcı bilgi veya veri araştırılması istiyorsa "arastirmaci" seç.
- Eğer aşama "arastirma_tamam" ise ve yazı/paragraf/rapor oluşturulması gerekiyorsa "yazar" seç.
- Eğer kullanıcı matematiksel bir işlem yapılmasını istiyorsa "hesaplayici" seç.
- Eğer aşama "yazim_tamam" veya "hesaplama_tamam" ise ve başka bir işlem gerekmiyorsa "bitir" seç.

Sadece şu dört kelimeden birini yaz:
arastirmaci
yazar
hesaplayici
bitir
"""

    cevap = model.invoke(karar_prompt)

    karar = cevap.content.strip().lower()

    print(f"\n[SUPERVISOR] Karar: {karar}")

    return {"sonraki": karar}



def arastirmaci_node(state: AgentState):
    print("[ARASTIRMACI] Çalışıyor...")

    cevap = model.invoke([
        {
            "role": "system",
            "content": (
                "Sen bir araştırmacısın. "
                "Sadece gerekli bilgileri araştırma notları halinde ver. "
                "Paragraf, makale veya son kullanıcıya yönelik metin yazma."
            )
        },
        *state["messages"]
    ])

    print("[ARASTIRMACI] İş tamamlandı.")

    return {
        "messages": [cevap],
        "asama": "arastirma_tamam"
    }


def yazar_node(state: AgentState):
    print("[YAZAR] Çalışıyor...")

    kullanici_istegi = state["messages"][0].content
    arastirma = state["messages"][-1].content

    cevap = model.invoke([
        {
            "role": "system",
            "content": (
                "Sen bir yazarsın. "
                "Araştırmacının verdiği bilgileri kullanarak "
                "akıcı ve kısa bir paragraf oluştur. "
                "Yeni bilgi uydurma."
            )
        },
        {
            "role": "user",
            "content": f"""
Kullanıcının isteği:
{kullanici_istegi}

Araştırmacının topladığı bilgiler:
{arastirma}

Bu bilgileri kullanarak kullanıcıya uygun akıcı bir paragraf yaz.
"""
        }
    ])

    print("[YAZAR] İş tamamlandı.")

    return {
        "messages": [cevap],
        "asama": "yazim_tamam"
    }

def hesaplayici_node(state: AgentState):
    print("[HESAPLAYICI] Çalışıyor...")

    kullanici_istegi = state["messages"][0].content

    hesaplama_prompt = f"""
Sen bir hesaplayıcısın.

Kullanıcının isteği:
{kullanici_istegi}

Gerekli matematik işlemini yap.
Sadece hesaplama sonucunu ver.
"""

    cevap = model.invoke([
        {
            "role": "system",
            "content": "Sen sadece matematik işlemleri yapan bir uzmansın."
        },
        {
            "role": "user",
            "content": hesaplama_prompt
        }
    ])

    print("[HESAPLAYICI] İş tamamlandı.")

    return {
        "messages": [cevap],
        "asama": "hesaplama_tamam"
    }

def yonlendir(
    state: AgentState
) -> Literal["arastirmaci", "yazar", "hesaplayici","__end__"]:

    karar = state["sonraki"]

    if "arastirmaci" in karar:
        return "arastirmaci"

    elif "yazar" in karar:
        return "yazar"

    elif "hesaplayici" in karar:
            return "hesaplayici"

    else:
        return END


graf = StateGraph(AgentState)


graf.add_node("supervisor", supervisor_node)
graf.add_node("arastirmaci", arastirmaci_node)
graf.add_node("yazar", yazar_node)
graf.add_node("hesaplayici", hesaplayici_node)


graf.set_entry_point("supervisor")


graf.add_conditional_edges(
    "supervisor",
    yonlendir,
    {
        "arastirmaci": "arastirmaci",
        "yazar": "yazar",
        "hesaplayici": "hesaplayici",
        END: END
    }
)


graf.add_edge("arastirmaci", "supervisor")
graf.add_edge("yazar", "supervisor")
graf.add_edge("hesaplayici", "supervisor")

app = graf.compile()


sonuc = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "125 ile 8'i çarp, sonra sonucu bir cümleye dönüştür"
            }
        ],
        "sonraki": "",
        "asama": "baslangic"
    },
    config={"recursion_limit": 10}
)

for m in sonuc["messages"]:
    print(m)
    print("---")


print(app.get_graph().draw_ascii())