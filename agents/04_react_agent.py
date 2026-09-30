import anthropic
import os
from dotenv import load_dotenv


load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

MODEL = "claude-sonnet-4-6"


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


tool_functions = {
    "calculator": run_calculator,
    "get_weather": run_weather
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
    }
]


react_system_prompt = """You are an assistant that solves a task step by step.

At each step, first explain BRIEFLY what you need to do,
then call a tool if needed.

Keep your thoughts to one sentence.
When you have enough information, give your final answer.
"""


def run_react_agent(question, max_steps=5):
    messages = [
        {
            "role": "user",
            "content": question
        }
    ]

    step = 0

    while step < max_steps:
        step += 1

        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=react_system_prompt,
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
                print(
                    f"[Step {step} - Thought/Answer]: "
                    f"{block.text}"
                )

        if response.stop_reason != "tool_use":
            break

        tool_results = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            function = tool_functions.get(block.name)

            print(
                f"[Step {step} - Action]: "
                f"{block.name}({block.input})"
            )

            if function is None:
                result = f"ERROR: There is no tool named '{block.name}'"

            else:
                try:
                    result = function(**block.input)

                except Exception as e:
                    result = f"ERROR: {str(e)}"

            print(
                f"[Step {step} - Observation]: {result}"
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

    if step >= max_steps:
        print("\n⚠️ Reached the maximum number of steps.")


if __name__ == "__main__":
    run_react_agent(
        "What is the weather like in Ankara? If the temperature is below 20, multiply it by 3, otherwise multiply it by 5."
    )