import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"


def run_calculator(operation, number1, number2):
    if operation == "add":
        return number1 + number2
    elif operation == "subtract":
        return number1 - number2
    elif operation == "multiply":
        return number1 * number2
    elif operation == "divide":
        return number1 / number2


def run_weather(city):
    dummy_data = {
        "Istanbul": "22°C, partly cloudy",
        "Ankara": "18°C, clear"
    }

    return dummy_data.get(city, "No data for this city")


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
        "description": "Returns the current weather for a city.",
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


messages = [
    {
        "role": "user",
        "content": "What is the weather like in Istanbul?"
    }
]


response = client.messages.create(
    model=MODEL,
    max_tokens=500,
    tools=tools,
    messages=messages
)


tool_block = None

for block in response.content:
    if block.type == "tool_use":
        tool_block = block
        break


if tool_block:
    if tool_block.name == "calculator":
        result = run_calculator(**tool_block.input)

    elif tool_block.name == "get_weather":
        result = run_weather(**tool_block.input)

    messages.append({
        "role": "assistant",
        "content": response.content
    })

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": str(result)
            }
        ]
    })

    final_response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=tools,
        messages=messages
    )

    print(final_response.content[0].text)

else:
    print(response.content[0].text)