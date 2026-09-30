import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

vo = voyageai.Client()

def fixed_size_chunk(text, chunk_size=200):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def overlap_chunk(text, chunk_size=200, overlap=30):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += chunk_size - overlap

    return chunks


def paragraph_chunk(text, max_size=500):
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if len(current_chunk) + len(paragraph) <= max_size:
            current_chunk += paragraph + "\n\n"

        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(
            current_chunk.strip()
        )

    return chunks


text = """Our company gives employees 14 days of annual leave per year.
Leave requests are sent to the manager for approval.
Employees can apply for leave through the company's human resources system.

Remote employees must use a VPN.
Company computers are updated regularly.
Employees must use a secure connection when they connect to company systems.

Salaries are paid at the end of each month.
Salary information is kept private for each employee.
Payslips can be viewed through each employee's personal account.

All employees must attend security training.
New employees learn the company policies during their first week.
Employees must use company resources for work purposes only.

Annual performance reviews take place at the end of each year.
Managers hold performance meetings with employees.
Performance results are used in employee development plans."""



chunks = fixed_size_chunk(
    text,
    chunk_size=200
)

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i}:")
    print(chunk)


chunks = overlap_chunk(
    text,
    chunk_size=200,
    overlap=30
)

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i}:")
    print(chunk)



chunks = paragraph_chunk(
    text,
    max_size=200
)

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i}:")
    print(chunk)


chunks = paragraph_chunk(
    text,
    max_size=250
)

chunk_result = vo.embed(
    chunks,
    model="voyage-4",
    input_type="document"
)

chunk_embeddings = chunk_result.embeddings


question = "How many days of annual leave are there?"

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


results = []

for i, chunk_vector in enumerate(chunk_embeddings):

    score = cosine_similarity(
        question_vector,
        chunk_vector
    )

    results.append(
        (score, chunks[i])
    )


results.sort(reverse=True)


for score, chunk in results:
    print(f"\nScore: {score:.4f}")
    print(chunk)


chunks_100 = paragraph_chunk(
    text,
    max_size=100
)

chunks_1000 = paragraph_chunk(
    text,
    max_size=1000
)

print(
    "Number of 100-character chunks:",
    len(chunks_100)
)

print(
    "Number of 1000-character chunks:",
    len(chunks_1000)
)