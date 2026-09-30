import anthropic
import time

from dotenv import load_dotenv
from anthropic import RateLimitError, APIError

load_dotenv()

client = anthropic.Anthropic()

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

        else:
            return f"ERROR: Unknown operation: {operation}"

    except Exception as e:

        return f"ERROR: Something went wrong during the calculation: {str(e)}"


def run_weather(city=None):

    if not city:
        return "ERROR: No city given"

    dummy_data = {
        "Istanbul": "22°C, partly cloudy",
        "Ankara": "18°C, clear"
    }

    if city not in dummy_data:

        available_cities = list(dummy_data.keys())

        return (
            f"ERROR: No data found for '{city}'. "
            f"Available cities: {available_cities}"
        )

    return dummy_data[city]

system_prompt = """
If a tool returns an error, give the user a short and direct answer.
Do not add extra explanations, emoji or unneeded suggestions.
"""

tools = [

    {
        "name": "calculator",

        "description": (
            "Adds, subtracts, "
            "multiplies or divides two numbers."
        ),

        "input_schema": {

            "type": "object",

            "properties": {

                "operation": {
                    "type": "string",
                    "enum": [
                        "add",
                        "subtract",
                        "multiply",
                        "divide"
                    ]
                },

                "number1": {
                    "type": "number"
                },

                "number2": {
                    "type": "number"
                }
            },

            "required": [
                "operation",
                "number1",
                "number2"
            ]
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

            "required": [
                "city"
            ]
        }
    }
]



tool_functions = {

    "calculator": run_calculator,
    "get_weather": run_weather
}

def safe_request(messages, attempts=3):

    for i in range(attempts):

        try:

            return client.messages.create(
                model=MODEL,
                max_tokens=500,
                tools=tools,
                system=system_prompt,
                messages=messages
            )

        except RateLimitError:

            wait_time = 2 ** i

            print(
                f"Hit the rate limit. "
                f"Waiting {wait_time} seconds..."
            )

            time.sleep(wait_time)

        except APIError as e:

            print(f"API error: {e}")

            raise

    raise Exception(
        "Reached the maximum number of API attempts."
    )

# messages = [

#     {
#         "role": "user",
#         "content": "What is the weather like in Paris?"
#     }

# ]

messages = [

    {
        "role": "user",
        "content": "Divide 10 by 0"
    }

]


MAX_STEPS = 5

step = 0


while step < MAX_STEPS:

    step += 1
    response = safe_request(messages)


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



        function = tool_functions.get(
            block.name
        )



        if function is None:

            result = (
                f"ERROR: There is no tool "
                f"named '{block.name}'"
            )


        else:

            try:

                result = function(**block.input)

            except Exception as e:

                result = (
                    "ERROR: Something went wrong "
                    f"while running the tool: {str(e)}"
                )


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

    print(
        "\nSorry, I could not finish this request. "
        "It needed too many steps."
    )