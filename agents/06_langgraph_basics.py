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
    step_count: int


def agent_node(state: AgentState):
    step_count = state.get("step_count", 0) + 1
    message = client.messages.create(
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

    answer = message.content[0].text

    return {
        "messages": [
            {
            "role": "assistant",
            "content": answer
            }
        ],
            "step_count": step_count
}


graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)

graph.set_entry_point("agent")

graph.add_edge("agent", END)

app = graph.compile()


result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Hello, briefly introduce yourself."
            }
        ],
        "step_count": 0
    }
)

print(result["messages"][-1])

print(app.get_graph().draw_ascii())
print("Step count:", result["step_count"])