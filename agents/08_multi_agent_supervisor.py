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
    next: str
    stage: str


def supervisor_node(state: AgentState):
    stage = state["stage"]

    decision_prompt = f"""
The user's request:

"{state["messages"][0].content}"

Current stage:
"{stage}"

Rules:

- If the user only sent a simple greeting, choose "finish".
- If the user wants information or data researched, choose "researcher".
- If the stage is "research_done" and a text/paragraph/report needs to be written, choose "writer".
- If the user wants a math operation done, choose "calculator".
- If the stage is "writing_done" or "calculation_done" and no other work is needed, choose "finish".

Write only one of these four words:
researcher
writer
calculator
finish
"""

    answer = model.invoke(decision_prompt)

    decision = answer.content.strip().lower()

    print(f"\n[SUPERVISOR] Decision: {decision}")

    return {"next": decision}



def researcher_node(state: AgentState):
    print("[RESEARCHER] Working...")

    answer = model.invoke([
        {
            "role": "system",
            "content": (
                "You are a researcher. "
                "Give only the needed information as research notes. "
                "Do not write paragraphs, articles or text for the end user."
            )
        },
        *state["messages"]
    ])

    print("[RESEARCHER] Task done.")

    return {
        "messages": [answer],
        "stage": "research_done"
    }


def writer_node(state: AgentState):
    print("[WRITER] Working...")

    user_request = state["messages"][0].content
    research = state["messages"][-1].content

    answer = model.invoke([
        {
            "role": "system",
            "content": (
                "You are a writer. "
                "Using the information from the researcher, "
                "write a short paragraph that reads well. "
                "Do not make up new information."
            )
        },
        {
            "role": "user",
            "content": f"""
The user's request:
{user_request}

Information gathered by the researcher:
{research}

Using this information, write a paragraph that reads well and fits the user's request.
"""
        }
    ])

    print("[WRITER] Task done.")

    return {
        "messages": [answer],
        "stage": "writing_done"
    }

def calculator_node(state: AgentState):
    print("[CALCULATOR] Working...")

    user_request = state["messages"][0].content

    calculation_prompt = f"""
You are a calculator.

The user's request:
{user_request}

Do the needed math operation.
Give only the result of the calculation.
"""

    answer = model.invoke([
        {
            "role": "system",
            "content": "You are an expert who only does math operations."
        },
        {
            "role": "user",
            "content": calculation_prompt
        }
    ])

    print("[CALCULATOR] Task done.")

    return {
        "messages": [answer],
        "stage": "calculation_done"
    }

def route(
    state: AgentState
) -> Literal["researcher", "writer", "calculator","__end__"]:

    decision = state["next"]

    if "researcher" in decision:
        return "researcher"

    elif "writer" in decision:
        return "writer"

    elif "calculator" in decision:
            return "calculator"

    else:
        return END


graph = StateGraph(AgentState)


graph.add_node("supervisor", supervisor_node)
graph.add_node("researcher", researcher_node)
graph.add_node("writer", writer_node)
graph.add_node("calculator", calculator_node)


graph.set_entry_point("supervisor")


graph.add_conditional_edges(
    "supervisor",
    route,
    {
        "researcher": "researcher",
        "writer": "writer",
        "calculator": "calculator",
        END: END
    }
)


graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", "supervisor")
graph.add_edge("calculator", "supervisor")

app = graph.compile()


result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Multiply 125 by 8, then turn the result into a sentence"
            }
        ],
        "next": "",
        "stage": "start"
    },
    config={"recursion_limit": 10}
)

for m in result["messages"]:
    print(m)
    print("---")


print(app.get_graph().draw_ascii())