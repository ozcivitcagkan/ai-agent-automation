from typing import Annotated, TypedDict, Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


load_dotenv()


MODEL = "claude-sonnet-4-6"

model = ChatAnthropic(model=MODEL)



BANNED_WORDS = [
    "password",
    "credit card",
    "passcode",
    "social security",
    "api key",
    "token",
    "access token",
    "connection string"
]


def is_input_safe(message: str) -> tuple[bool, str]:

    message_lower = message.lower()

    for word in BANNED_WORDS:
        if word in message_lower:
            return False, f"This request cannot be processed because it contains '{word}'."

    if len(message) > 2000:
        return False, "The message is too long, please shorten it."

    return True, ""


def is_output_safe(answer: str) -> tuple[bool, str]:

    if not answer or not answer.strip():
        return False, "An empty answer was produced."

    if len(answer) > 5000:
        return False, "The answer is longer than expected."

    sensitive_patterns = [
        "api_key",
        "sk-ant-",
        "password="
    ]

    for pattern in sensitive_patterns:
        if pattern in answer.lower():
            return False, "Sensitive information was found in the answer."

    return True, ""



class CostTracker:

    def __init__(self, limit_usd=0.10):

        self.total_cost = 0.0
        self.limit = limit_usd

    def add(self, input_tokens, output_tokens):

        cost = (
            (input_tokens / 1_000_000 * 3)
            +
            (output_tokens / 1_000_000 * 15)
        )

        self.total_cost += cost

        print(
            f"[COST] This call: ${cost:.6f} | "
            f"Total: ${self.total_cost:.6f}"
        )

        if self.total_cost > self.limit:
            raise RuntimeError(
                f"Cost limit exceeded: "
                f"${self.total_cost:.6f}"
            )

        return self.total_cost

tracker = CostTracker(limit_usd=0.1)



def call_model(model_input):

    message = model.invoke(model_input)

    input_tokens = message.usage_metadata.get(
        "input_tokens",
        0
    )

    output_tokens = message.usage_metadata.get(
        "output_tokens",
        0
    )

    tracker.add(
        input_tokens,
        output_tokens
    )

    return message



class AgentState(TypedDict):

    messages: Annotated[list, add_messages]
    next: str
    stage: str



def supervisor_node(state: AgentState):

    user_request = state["messages"][0].content
    stage = state["stage"]

    decision_prompt = f"""
The user's request:

"{user_request}"

Current stage:

"{stage}"

Route the task using the rules below:

- If a math operation is needed, choose "calculator".
- If information or data needs to be researched, choose "researcher".
- If research or calculation is done and the result
  should be turned into a text, paragraph, report or summary,
  choose "writer".
- If the user wants a file deleted, choose "delete_data".
- If the work is done, choose "finish".
- If the user is only greeting, choose "finish".

Write only one of these words:

researcher
writer
calculator
delete_data
finish
"""

    answer = call_model(decision_prompt)

    decision = answer.content.strip().lower()

    print(f"\n[SUPERVISOR] Decision: {decision}")

    return {
        "next": decision
    }



def researcher_node(state: AgentState):

    print("[RESEARCHER] Working...")

    user_request = state["messages"][0].content

    answer = call_model([
        {
            "role": "system",
            "content": (
                "You are a researcher. "
                "Prepare short and clear research notes "
                "on the topic the user asked about. "
                "Do not write paragraphs or end-user text."
            )
        },
        {
            "role": "user",
            "content": user_request
        }
    ])

    print("[RESEARCHER] Task done.")

    return {
        "messages": [answer],
        "stage": "research_done"
    }



def calculator_node(state: AgentState):

    print("[CALCULATOR] Working...")

    user_request = state["messages"][0].content

    answer = call_model([
        {
            "role": "system",
            "content": (
                "You are a calculator. "
                "Do the math operation and "
                "give only the result."
            )
        },
        {
            "role": "user",
            "content": user_request
        }
    ])

    print("[CALCULATOR] Task done.")

    return {
        "messages": [answer],
        "stage": "calculation_done"
    }


def writer_node(state: AgentState):

    print("[WRITER] Working...")

    user_request = state["messages"][0].content
    expert_result = state["messages"][-1].content

    answer = call_model([
        {
            "role": "system",
            "content": (
                "You are a writer. "
                "Using the information given by the expert, "
                "write a short text that reads well. "
                "Do not make up new information."
            )
        },
        {
            "role": "user",
            "content": f"""
The user's request:

{user_request}

The result given by the expert:

{expert_result}

Using this information, write a text that fits the user's request.
"""
        }
    ])

    print("[WRITER] Task done.")

    return {
        "messages": [answer],
        "stage": "writing_done"
    }



def delete_data(file_name: str):

    print(
        f"[FAKE TOOL] Deleting '{file_name}'..."
    )

    return (
        f"[SIMULATION] '{file_name}' "
        "was deleted successfully."
    )



def delete_data_node(state: AgentState):

    print("[DELETE_DATA] Risky operation detected.")

    user_request = state["messages"][0].content

    file_name = "test.txt"

    print(
        f"\nThe agent wants to do this:"
        f"\n'{user_request}'"
    )

    print(
        f"\nFile to delete: {file_name}"
    )

    approval = input(
        "Do you approve this operation? (y/n): "
    ).strip().lower()

    if approval != "y":

        print("[DELETE_DATA] Operation rejected.")

        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": (
                        "The delete operation was not "
                        "approved by the user."
                    )
                }
            ],
            "stage": "delete_rejected"
        }

    result = delete_data(file_name)

    print("[DELETE_DATA] Operation done.")

    return {
        "messages": [
            {
                "role": "assistant",
                "content": result
            }
        ],
        "stage": "delete_done"
    }



def route(
    state: AgentState
) -> Literal[
    "researcher",
    "writer",
    "calculator",
    "delete_data",
    "__end__"
]:

    decision = state["next"]

    if "researcher" in decision:
        return "researcher"

    elif "writer" in decision:
        return "writer"

    elif "calculator" in decision:
        return "calculator"

    elif "delete_data" in decision:
        return "delete_data"

    else:
        return END



graph = StateGraph(AgentState)


graph.add_node(
    "supervisor",
    supervisor_node
)

graph.add_node(
    "researcher",
    researcher_node
)

graph.add_node(
    "writer",
    writer_node
)

graph.add_node(
    "calculator",
    calculator_node
)

graph.add_node(
    "delete_data",
    delete_data_node
)


graph.set_entry_point("supervisor")


graph.add_conditional_edges(
    "supervisor",
    route,
    {
        "researcher": "researcher",
        "writer": "writer",
        "calculator": "calculator",
        "delete_data": "delete_data",
        END: END
    }
)


graph.add_edge(
    "researcher",
    "supervisor"
)

graph.add_edge(
    "calculator",
    "supervisor"
)

graph.add_edge(
    "writer",
    "supervisor"
)

graph.add_edge(
    "delete_data",
    "supervisor"
)


app = graph.compile()




def run_system(user_message: str):

    # 1. INPUT GUARDRAIL

    safe, reason = is_input_safe(
        user_message
    )

    if not safe:

        print("\n[INPUT GUARDRAIL] Request rejected.")
        print(f"Reason: {reason}")

        return


    # 2. AGENT SYSTEM

    try:

        result = app.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "next": "",
                "stage": "start"
            },
            config={
                "recursion_limit": 10
            }
        )

    except RuntimeError as error:

        print("\n[RESOURCE GUARDRAIL]")
        print(error)

        return


    # 3. OUTPUT GUARDRAIL

    last_message = result["messages"][-1]

    if hasattr(last_message, "content"):
        final_answer = last_message.content
    else:
        final_answer = str(last_message)


    safe, reason = is_output_safe(
        final_answer
    )


    if not safe:

        print(
            "\n[OUTPUT GUARDRAIL] "
            "The answer was not shown to the user."
        )

        print(
            f"Reason: {reason}"
        )

        return


    print("\n===== FINAL ANSWER =====")
    print(final_answer)

    print(
        f"\nTotal cost: "
        f"${tracker.total_cost:.6f}"
    )


# TESTS

USER_MESSAGE = (
    "save the connection string details"
)

run_system(USER_MESSAGE)

