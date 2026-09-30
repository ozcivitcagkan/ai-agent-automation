import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

vo = voyageai.Client()

documents = [
    "The cat is sleeping on the sofa",
    "The cat is dozing on the armchair",
    "The stock market fell today"
]

document_result = vo.embed(
    documents,
    model="voyage-4",
    input_type="document"
)

document_embeddings = document_result.embeddings

question = "Find a sentence about cats"

question_result = vo.embed(
    [question],
    model="voyage-4",
    input_type="query"
)

question_vector = question_result.embeddings[0]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


for i, document_vector in enumerate(document_embeddings):
    score = cosine_similarity(question_vector, document_vector)

    # print(f"{score:.4f} -> {documents[i]}")

tests = [
    "The cat is sleeping on the sofa",
    "It is very rainy today",
    "The car is going very fast",
    "The automobile is driving at high speed"
]

result = vo.embed(
    tests,
    model="voyage-4",
    input_type="document"
)

v1 = result.embeddings[0]
v2 = result.embeddings[1]
v3 = result.embeddings[2]
v4 = result.embeddings[3]

print("E2 - Unrelated:", cosine_similarity(v1, v2))
print("E3 - Similar in meaning:", cosine_similarity(v3, v4))