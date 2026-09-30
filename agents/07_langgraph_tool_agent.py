from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


load_dotenv()


MODEL = "claude-sonnet-4-6"


@tool("calculator")
def run_calculator(operation: str, number1: float, number2: float):
    """Adds, subtracts, multiplies or divides two numbers."""
    try:
        if operation in ["add", "+"]:
            return number1 + number2

        elif operation in ["subtract", "-"]:
            return number1 - number2

        elif operation in ["multiply", "*"]:
            return number1 * number2

        elif operation in ["divide", "/"]:
            if number2 == 0:
                return "ERROR: Cannot divide by zero"

            return number1 / number2

        return f"ERROR: Invalid operation: {operation}"

    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def run_weather(city: str):
    """Returns the weather for a city."""
    if not city:
        return "ERROR: No city given"

    dummy_data = {
        "Istanbul": "22°C, partly cloudy",
        "Ankara": "18°C, clear"
    }

    return dummy_data.get(
        city,
        f"ERROR: No data for '{city}'. "
        f"Available: {list(dummy_data.keys())}"
    )


tools = [
    run_calculator,
    run_weather
]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatAnthropic(
    model=MODEL
)

model_with_tools = model.bind_tools(tools)


def agent_node(state: AgentState):
    message = model_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [message]
    }


tools_node = ToolNode(tools)


graph = StateGraph(AgentState)


graph.add_node("agent", agent_node)

graph.add_node("tools", tools_node)


graph.set_entry_point("agent")


graph.add_conditional_edges(
    "agent",
    tools_condition
)


graph.add_edge(
    "tools",
    "agent"
)


app = graph.compile()


result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Find the temperature in Istanbul, then multiply it by 2."
            }
        ]
    }
)


for message in result["messages"]:
    print(message)


print(app.get_graph().draw_ascii())