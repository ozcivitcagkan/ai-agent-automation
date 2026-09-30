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
        "content": "Find the temperature in Istanbul and then multiply that temperature by 7."
    }
]


MAX_STEPS = 5
step = 0


while step < MAX_STEPS:

    step += 1

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=tools,
        messages=messages
    )

    messages.append({
        "role": "assistant",
        "content": response.content
    })

    if response.stop_reason != "tool_use":

        for block in response.content:
            if block.type == "text":
                print(block.text)

        break

    tool_results = []

    for block in response.content:

        if block.type != "tool_use":
            continue

        print(f"Tool called: {block.name}")
        print(f"Input: {block.input}")

        if block.name == "calculator":

            result = run_calculator(**block.input)

        elif block.name == "get_weather":

            result = run_weather(**block.input)

        else:

            result = f"Unknown tool: {block.name}"

        print(f"Tool result: {result}")

        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": str(result)
        })

    messages.append({
        "role": "user",
        "content": tool_results
    })



if step >= MAX_STEPS:

    print(f"Agent reached the MAX_STEPS limit: {MAX_STEPS}")