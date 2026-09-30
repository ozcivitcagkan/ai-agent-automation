import voyageai
import chromadb
from dotenv import load_dotenv


load_dotenv()

vo = voyageai.Client()

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



chunks = [
    "Our company gives employees 14 days of annual leave per year.",
    "Remote employees must use a VPN.",
    "Salaries are paid at the end of each month.",
    "All employees must attend security training.",
    "Annual performance reviews take place at the end of each year."
]


embeddings = voyage_embed_document(
    chunks
)

collection.add(
    ids=[
        "chunk_0",
        "chunk_1",
        "chunk_2",
        "chunk_3",
        "chunk_4"
    ],

    embeddings=embeddings,

    documents=chunks,

    metadatas=[
        {
            "source": "company_policies.txt",
            "chunk_no": 0,
            "category": "leave"
        },
        {
            "source": "company_policies.txt",
            "chunk_no": 1,
            "category": "vpn"
        },
        {
            "source": "company_policies.txt",
            "chunk_no": 2,
            "category": "salary"
        },
        {
            "source": "company_policies.txt",
            "chunk_no": 3,
            "category": "security"
        },
        {
            "source": "company_policies.txt",
            "chunk_no": 4,
            "category": "performance"
        }
    ]
)


print(collection.count())


question = "How many days of annual leave are there?"


question_vector = voyage_embed_query(
    question
)


results = collection.query(
    query_embeddings=[question_vector],
    n_results=3
)


print(results["documents"])

print(results["distances"])

print(results["metadatas"])



filtered_results = collection.query(
    query_embeddings=[question_vector],
    n_results=3,
    where={
        "category": "leave"
    }
)


print(
    filtered_results["documents"]
)

# collection.delete(
#     ids=["chunk_1"]
# )



# collection.update(
#     ids=["chunk_0"],
#     documents=[
#         "Our company gives employees 20 days of annual leave per year."
#     ]
# )