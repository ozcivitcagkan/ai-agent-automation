import anthropic
import os
import json
from dotenv import load_dotenv


load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

MODEL = "claude-sonnet-4-6"

MEMORY_FILE = "agent_memory.json"


def run_calculator(operation, number1, number2):
    try:
        if operation == "add":
            return number1 + number2

        elif operation == "subtract":
            return number1 - number2

        elif operation == "multiply":
            return number1 * number2

        elif operation == "divide":
            if number2 == 0:
                return "ERROR: Cannot divide by zero"

            return number1 / number2

    except Exception as e:
        return f"ERROR: {str(e)}"


def run_weather(city=None):
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


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def write_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            ensure_ascii=False,
            indent=2
        )


def run_save_to_memory(key, value):
    memory = load_memory()

    memory[key] = value

    write_memory(memory)

    return f"Saved: {key} = {value}"


def run_read_from_memory(key):
    memory = load_memory()

    return memory.get(
        key,
        f"No saved information for '{key}'"
    )


tool_functions = {
    "calculator": run_calculator,
    "get_weather": run_weather,
    "save_to_memory": run_save_to_memory,
    "read_from_memory": run_read_from_memory
}


tools = [
    {
        "name": "calculator",
        "description": "Adds, subtracts, multiplies or divides two numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "number1": {
                    "type": "number"
                },
                "number2": {
                    "type": "number"
                }
            },
            "required": ["operation", "number1", "number2"]
        }
    },
    {
        "name": "get_weather",
        "description": "Returns the weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "save_to_memory",
        "description": "Saves a lasting fact about the user that should be remembered later. For example a name or a preference.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "A short name for the fact. For example name."
                },
                "value": {
                    "type": "string",
                    "description": "The information to save."
                }
            },
            "required": ["key", "value"]
        }
    },
    {
        "name": "read_from_memory",
        "description": "Reads a fact that was saved to long-term memory earlier.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                }
            },
            "required": ["key"]
        }
    }
]


def build_react_system_prompt():
    memory = load_memory()

    memory_text = ""

    if memory:
        memory_text = "\n\nWhat you know about the user:\n"

        for key, value in memory.items():
            memory_text += f"- {key}: {value}\n"

    return f"""You are an assistant that solves a task step by step.

At each step, first explain briefly what you need to do,
then call a tool if needed.

Keep your thoughts to one sentence.

If the user shares a lasting fact about themselves
(such as a name or preference that should be remembered),
use the save_to_memory tool.

When needed, check previously saved facts
with the read_from_memory tool.

When you have enough information, give your final answer.
{memory_text}"""


def start_react_agent():
    messages = []

    print("Agent ready. Type 'q' to quit.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in ["q", "exit", "quit"]:
            print("See you!")
            break

        if not question:
            continue

        messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        step = 0

        while step < 5:
            step += 1

            response = client.messages.create(
                model=MODEL,
                max_tokens=500,
                system=build_react_system_prompt(),
                tools=tools,
                messages=messages
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": response.content
                }
            )

            for block in response.content:
                if block.type == "text" and block.text.strip():
                    print(f"[Step {step}]: {block.text}")

            if response.stop_reason != "tool_use":
                break

            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                function = tool_functions.get(block.name)

                if function is None:
                    result = f"ERROR: '{block.name}' does not exist"

                else:
                    try:
                        result = function(**block.input)

                    except Exception as e:
                        result = f"ERROR: {str(e)}"

                print(
                    f"[Action]: {block.name}({block.input}) → {result}"
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": tool_results
                }
            )

        print()


if __name__ == "__main__":
    start_react_agent()