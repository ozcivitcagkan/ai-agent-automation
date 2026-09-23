from typing import TypedDict, Annotated

import anthropic
import os

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

MODEL = "claude-sonnet-4-6"


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    adim_sayisi: int


def agent_node(state: AgentState):
    adim_sayisi = state.get("adim_sayisi", 0) + 1
    mesaj = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    m.content
                    if hasattr(m, "content")
                    else m["content"]
                )
            }
            for m in state["messages"]
        ]
    )

    cevap = mesaj.content[0].text

    return {
        "messages": [
            {
            "role": "assistant",
            "content": cevap
            }
        ],
            "adim_sayisi": adim_sayisi
}


graf = StateGraph(AgentState)

graf.add_node("agent", agent_node)

graf.set_entry_point("agent")

graf.add_edge("agent", END)

app = graf.compile()


sonuc = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Merhaba, kısaca kendini tanıt."
            }
        ],
        "adim_sayisi": 0
    }
)

print(sonuc["messages"][-1])

print(app.get_graph().draw_ascii())
print("Adım sayısı:", sonuc["adim_sayisi"])