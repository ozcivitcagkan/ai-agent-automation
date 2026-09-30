import os
import voyageai
import chromadb
import anthropic

from dotenv import load_dotenv


load_dotenv()

MODEL = "claude-haiku-4-5"


RUN_TASK_A = False
RUN_TASK_B = False
RUN_TASK_C = False
RUN_TASK_D = False
RUN_TASK_E = True


vo = voyageai.Client()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

client_db = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client_db.get_or_create_collection(
    name="company_policies"
)


def voyage_embed_query(text):
    result = vo.embed(
        [text],
        model="voyage-4",
        input_type="query"
    )

    return result.embeddings[0]



def find_relevant_chunks_detailed(question, n=3):

    question_vector = voyage_embed_query(question)

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=n
    )

    detailed = []

    for i, document in enumerate(
        results["documents"][0]
    ):

        detailed.append(
            {
                "text": document,
                "category": results["metadatas"][0][i]["category"]
            }
        )

    return detailed


test_questions = [
    {
        "question": "How many days of annual leave are there?",
        "expected_category": "leave"
    },
    {
        "question": "When are salaries paid?",
        "expected_category": "salary"
    },
    {
        "question": "Is using a VPN required?",
        "expected_category": "vpn"
    },
    {
        "question": "When do performance reviews take place?",
        "expected_category": "performance"
    },
    {
        "question": "Is security training required for employees?",
        "expected_category": "security"
    }
]


if RUN_TASK_A:

    correct_count = 0

    for test in test_questions:

        detailed = find_relevant_chunks_detailed(
            test["question"],
            n=1
        )

        found_category = detailed[0]["category"]

        is_correct = (
            found_category
            == test["expected_category"]
        )

        if is_correct:
            correct_count += 1

        print(
            f"{'✅' if is_correct else '❌'} "
            f"{test['question']}"
        )

        print(
            f"   Expected: {test['expected_category']} "
            f"| Found: {found_category}"
        )

    print(
        f"\nAccuracy: "
        f"{correct_count}/{len(test_questions)}"
    )

    print(
        f"Rate: "
        f"{correct_count / len(test_questions) * 100:.1f}%"
    )




if RUN_TASK_B:

    for k in [1, 2, 3]:

        correct_count = 0

        for test in test_questions:

            detailed = find_relevant_chunks_detailed(
                test["question"],
                n=k
            )

            categories = [
                d["category"]
                for d in detailed
            ]

            is_correct = (
                test["expected_category"]
                in categories
            )

            if is_correct:
                correct_count += 1

        rate = (
            correct_count
            / len(test_questions)
            * 100
        )

        print(
            f"precision@{k}: "
            f"{correct_count}/{len(test_questions)} "
            f"({rate:.1f}%)"
        )



def build_rag_prompt(question, chunks):

    context = "\n\n".join(chunks)

    prompt = f"""Answer the question using the context below.

Use only the information in the context.
If the answer is not in the context, say "I don't have this information".
Do not make anything up.
If the user makes a wrong assumption,
correct it with the right information from the context.

Context:
{context}

Question:
{question}

Answer:
"""

    return prompt



def generation_test(
    question,
    correct_chunk,
    expected_keyword
):

    prompt = build_rag_prompt(
        question,
        [correct_chunk]
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = message.content[0].text

    passed = (
        expected_keyword.lower()
        in answer.lower()
    )

    print(
        f"{'✅' if passed else '❌'} "
        f"{question}"
    )

    print(
        f"   Answer: {answer}"
    )

    return passed


if RUN_TASK_C:


    generation_test(
        question="How many days of annual leave are there?",
        correct_chunk=(
            "Our company gives employees "
            "14 days of annual leave per year."
        ),
        expected_keyword="14"
    )

    generation_test(
        question="When are salaries paid?",
        correct_chunk=(
            "Salaries are paid at the end "
            "of each month."
        ),
        expected_keyword="month"
    )

    generation_test(
        question="What is the rule for remote employees?",
        correct_chunk=(
            "Remote employees must use "
            "a VPN."
        ),
        expected_keyword="VPN"
    )


def ask_rag(question, n=3):

    detailed = find_relevant_chunks_detailed(
        question,
        n=n
    )

    chunks = [
        d["text"]
        for d in detailed
    ]

    prompt = build_rag_prompt(
        question,
        chunks
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = message.content[0].text

    return answer, chunks



if RUN_TASK_D:


    end_to_end_tests = [
        {
            "question": "How many days of annual leave are there?",
            "expected": "14"
        },
        {
            "question": "When are salaries paid?",
            "expected": "month"
        },
        {
            "question": "What is the rule for remote employees?",
            "expected": "VPN"
        },
        {
            "question": "Who is the company's CEO?",
            "expected": "don't have"
        },
        {
            "question": "Is annual leave 30 days?",
            "expected": "14"
        }
    ]

    passed_count = 0

    for test in end_to_end_tests:

        answer, chunks = ask_rag(
            test["question"],
            n=3
        )

        passed = (
            test["expected"].lower()
            in answer.lower()
        )

        if passed:
            passed_count += 1

        print(
            f"\n{'✅' if passed else '❌'} "
            f"{test['question']}"
        )

        print(
            f"Answer: {answer}"
        )

    rate = (
        passed_count
        / len(end_to_end_tests)
        * 100
    )

    print(
        f"\nTotal passed: "
        f"{passed_count}/"
        f"{len(end_to_end_tests)}"
    )

    print(
        f"Pass rate: {rate:.1f}%"
    )




def paragraph_chunk(text, max_size=500):

    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if (
            len(current_chunk)
            + len(paragraph)
            <= max_size
        ):

            current_chunk += (
                paragraph + "\n\n"
            )

        else:

            if current_chunk:
                chunks.append(
                    current_chunk.strip()
                )

            current_chunk = (
                paragraph + "\n\n"
            )

    if current_chunk:
        chunks.append(
            current_chunk.strip()
        )

    return chunks



if RUN_TASK_E:


    text = """Our company gives employees 14 days of annual leave per year.
Leave requests are sent to the manager for approval.

Remote employees must use a VPN.
Company computers are updated regularly.

Salaries are paid at the end of each month.
Salary information is kept private for each employee.

All employees must attend security training.
New employees learn the company policies during their first week.

Annual performance reviews take place at the end of each year.
Managers hold performance meetings with employees."""

    small_chunks = paragraph_chunk(
        text,
        max_size=50
    )

    print(
        "\nNumber of chunks created:",
        len(small_chunks)
    )

    for i, chunk in enumerate(
        small_chunks
    ):

        print(f"\nChunk {i}:")
        print(chunk)