from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


load_dotenv()


MODEL = "claude-sonnet-4-6"


@tool
def hesap_makinesi_calistir(islem: str, sayi1: float, sayi2: float):
    """İki sayı arasında toplama, çıkarma, çarpma veya bölme işlemi yapar."""
    try:
        if islem in ["topla", "+"]:
            return sayi1 + sayi2

        elif islem in ["cikar", "çıkar", "-"]:
            return sayi1 - sayi2

        elif islem in ["carp", "çarp", "çarpma", "*"]:
            return sayi1 * sayi2

        elif islem in ["bol", "böl", "bölme", "/"]:
            if sayi2 == 0:
                return "HATA: Sıfıra bölme yapılamaz"

            return sayi1 / sayi2

        return f"HATA: Geçersiz işlem: {islem}"

    except Exception as e:
        return f"HATA: {str(e)}"


@tool
def hava_durumu_calistir(sehir: str):
    """Bir şehrin hava durumunu verir."""
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


araclar = [
    hesap_makinesi_calistir,
    hava_durumu_calistir
]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatAnthropic(
    model=MODEL
)

model_with_tools = model.bind_tools(araclar)


def agent_node(state: AgentState):
    mesaj = model_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [mesaj]
    }


tools_node = ToolNode(araclar)


graf = StateGraph(AgentState)


graf.add_node("agent", agent_node)

graf.add_node("tools", tools_node)


graf.set_entry_point("agent")


graf.add_conditional_edges(
    "agent",
    tools_condition
)


graf.add_edge(
    "tools",
    "agent"
)


app = graf.compile()


sonuc = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "İstanbul'daki sıcaklığı öğren, sonra bunu 2 ile çarp."
            }
        ]
    }
)


for mesaj in sonuc["messages"]:
    print(mesaj)


print(app.get_graph().draw_ascii())