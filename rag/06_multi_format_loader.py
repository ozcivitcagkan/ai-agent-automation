import os
import glob
import voyageai
import chromadb
import anthropic

from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document


load_dotenv()

MODEL = "claude-haiku-4-5"


client_db = chromadb.PersistentClient(path="./chroma_db")

collection = client_db.get_or_create_collection(
    name="real_files"
)

vo = voyageai.Client()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)



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
        chunks.append(current_chunk.strip())

    return chunks



def read_txt(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()



def read_pdf(file_path):
    reader = PdfReader(file_path)

    full_text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        full_text += page_text + "\n"

    return full_text




def read_docx(file_path):
    document = Document(file_path)

    full_text = ""

    for paragraph in document.paragraphs:
        full_text += paragraph.text + "\n"

    return full_text


def read_file(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return read_txt(file_path)

    elif extension == ".pdf":
        return read_pdf(file_path)

    elif extension == ".docx":
        return read_docx(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
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



def add_file_to_collection(
    file_path,
    collection_name="real_files"
):
    text = read_file(file_path)

    chunks = paragraph_chunk(
        text,
        max_size=500
    )

    if not chunks:
        print(f"No text found in file: {file_path}")
        return

    embeddings = voyage_embed_document(
        chunks
    )

    file_name = os.path.basename(
        file_path
    )

    ids = [
        f"{file_name}_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "source": file_name,
            "chunk_no": i
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

    print(
        f"{len(chunks)} chunks added: {file_name}"
    )



def add_all_files_in_folder(folder_path):
    files = (
        glob.glob(
            os.path.join(folder_path, "*.txt")
        )
        + glob.glob(
            os.path.join(folder_path, "*.pdf")
        )
        + glob.glob(
            os.path.join(folder_path, "*.docx")
        )
    )

    for file in files:
        add_file_to_collection(file)




def find_relevant_chunks_detailed(
    question,
    n=3
):
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
                "source": results["metadatas"][0][i]["source"],
                "chunk_no": results["metadatas"][0][i]["chunk_no"]
            }
        )

    return detailed



def build_rag_prompt(
    question,
    chunks
):
    context = "\n\n".join(
        [chunk["text"] for chunk in chunks]
    )

    sources = "\n".join(
        [
            f"- {chunk['source']} / chunk {chunk['chunk_no']}"
            for chunk in chunks
        ]
    )

    prompt = f"""Answer the question using the context below.

Use only the information in the context.
If the answer is not in the context, say "I don't have this information".
Do not make anything up.

Context:
{context}

Question:
{question}

Sources:
{sources}

Answer:
"""

    return prompt


def ask_rag(question, n=3):
    chunks = find_relevant_chunks_detailed(
        question,
        n=n
    )

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



if __name__ == "__main__":

    file = "leave_policy.txt"

    txt_text = read_txt(file)

    print(txt_text)


    pdf_text = read_pdf(
        "leave_policy.pdf"
    )

    print(pdf_text)


    print(
        "\nTXT length:",
        len(
            read_file(
                "leave_policy.txt"
            )
        )
    )

    print(
        "PDF length:",
        len(
            read_file(
                "leave_policy.pdf"
            )
        )
    )

    print(
        "DOCX length:",
        len(
            read_file(
                "leave_policy.docx"
            )
        )
    )



    print("\n===== TASK D: CHROMA =====")

    previous_count = collection.count()

    print(
        "Previous record count:",
        previous_count
    )

    add_file_to_collection(
        "leave_policy.txt"
    )

    next_count = collection.count()

    print(
        "Next record count:",
        next_count
    )


    question = "How many days of annual leave are there?"

    answer, sources = ask_rag(
        question,
        n=3
    )

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)

    print("\nSources used:")

    for source in sources:
        print(
            f"- {source['source']} "
            f"/ chunk {source['chunk_no']}"
        )


    previous_count = collection.count()

    print(
        "First count:",
        previous_count
    )

    add_file_to_collection(
        "leave_policy.txt"
    )

    next_count = collection.count()

    print(
        "Second count:",
        next_count
    )

    if next_count == previous_count:
        print(
            "The record count did not grow because the IDs are the same."
        )
    else:
        print(
            "The record count changed. "
            "Check how IDs behave in the Chroma result."
        )
