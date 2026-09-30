import os
import numpy as np
import voyageai
import chromadb
import anthropic

from dotenv import load_dotenv


load_dotenv()

MODEL = "claude-haiku-4-5"

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

def voyage_embed_document(texts):
    result = vo.embed(
        texts,
        model="voyage-4",
        input_type="document"
    )

    return result.embeddings


def voyage_embed_query(text):
    result = vo.embed(
        [text],
        model="voyage-4",
        input_type="query"
    )

    return result.embeddings[0]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def find_relevant_chunks(question, n=3):

    question_vector = voyage_embed_query(question)

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=n
    )

    return results["documents"][0]


def build_rag_prompt(question, chunks):

    context = "\n\n".join(chunks)

    prompt = f"""Answer the question using the context below.

Use only the information in the context.
If the answer is not in the context, say "I don't have this information".
Do not make anything up.
If the user makes a wrong assumption, correct it with the right information from the context.

Context:
{context}

Question:
{question}

Answer:
"""

    return prompt



def ask_rag(question, n=3):

    chunks = find_relevant_chunks(
        question,
        n
    )

    prompt = build_rag_prompt(
        question,
        chunks
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = message.content[0].text

    return answer, chunks


# question = "When are salaries paid?"

# chunks = find_relevant_chunks(
#     question,
#     n=3
# )

# print("\nQuestion:", question)

# for i, chunk in enumerate(chunks):
#     print(f"\nChunk {i}:")
#     print(chunk)



# question = "How many days of annual leave are there?"

# chunks = find_relevant_chunks(
#     question,
#     n=3
# )

# prompt = build_rag_prompt(
#     question,
#     chunks
# )

# print("\nPrompt to send to Claude:")
# print(prompt)


questions = [
    "How many days of annual leave are there?",
    "When are salaries paid?",
    "What is the rule for remote employees?"
]

for question in questions:

    answer, used_chunks = ask_rag(
        question,
        n=3
    )

    print("\n--------------------------------")
    print("QUESTION:", question)
    print("--------------------------------")

    print("\nANSWER:")
    print(answer)

    print("\nUSED CHUNKS:")

    for chunk in used_chunks:
        print("-", chunk)


# question = "Who is the company's CEO?"

# answer, used_chunks = ask_rag(
#     question,
#     n=3
# )

# print("\nQUESTION:")
# print(question)

# print("\nANSWER:")
# print(answer)

# question = "Is annual leave 30 days?"

# answer, used_chunks = ask_rag(
#     question,
#     n=3
# )

# print("\nQUESTION:")
# print(question)

# print("\nANSWER:")
# print(answer)


def find_relevant_chunks_detailed(question, n=3):

    question_vector = voyage_embed_query(
        question
    )

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


# question = "How many days of annual leave are there?"

# detailed_results = find_relevant_chunks_detailed(
#     question,
#     n=3
# )

# print("\nQuestion:", question)

# for result in detailed_results:

#     print("\nText:")
#     print(result["text"])

#     print("Category:")
#     print(result["category"])

#  The last two prompts hit the rpm limit, check them later.