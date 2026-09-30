# AI Agent Patterns

Small, runnable Python scripts that build up LLM agent and RAG patterns step by step,
using the Anthropic API, LangGraph and ChromaDB. Each file adds one idea on top of the
previous one. The commit history follows the same order.

For a complete project that uses these ideas together (multi-agent workflow, tool
permissions, guardrails, human approval, tests), see
[AI Marketplace Listing Assistant](https://github.com/ozcivitcagkan/AI-Marketplace-Listing-Assistant).

## Agents

| File | What it shows |
|---|---|
| `agents/01_chain_of_thought.py` | Step-by-step reasoning prompt, then function calling with a calculator and a mock weather tool |
| `agents/02_multi_step_tool_use.py` | Agent loop that calls several tools until the task is done |
| `agents/03_error_handling_retry.py` | Retry with backoff on rate limit and API errors, safe tool execution |
| `agents/04_react_agent.py` | ReAct loop with visible thought, action and observation steps and a step limit |
| `agents/05_agent_memory.py` | Short-term session history plus long-term memory saved to a JSON file through tools |
| `agents/06_langgraph_basics.py` | First LangGraph graph: state, nodes and edges |
| `agents/07_langgraph_tool_agent.py` | The same agent rebuilt with LangChain tools and `ToolNode` |
| `agents/08_multi_agent_supervisor.py` | Supervisor that routes work to researcher, writer and calculator agents |
| `agents/09_guardrails_agent.py` | Input and output checks, a per-run cost limit, recursion limit and human approval before a destructive action |

## RAG

| File | What it shows |
|---|---|
| `rag/01_embeddings_similarity.py` | Voyage AI embeddings and cosine similarity search |
| `rag/02_chunking.py` | Fixed-size, overlapping and paragraph-based chunking |
| `rag/03_chroma_vector_store.py` | Persistent vector store with ChromaDB and metadata |
| `rag/04_rag_pipeline.py` | End-to-end retrieval and answer generation with source citation |
| `rag/05_rag_evaluation.py` | Retrieval accuracy and generation quality checks on a small test set |
| `rag/06_multi_format_loader.py` | Loading TXT, PDF and DOCX files into the vector store with stable ids |

The `rag/izin_politikasi.*` files are a short synthetic company leave policy used as sample data.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then add your API keys
```

Run a script from its own folder so relative paths resolve:

```bash
cd agents
python 04_react_agent.py
```

## Notes

- This is a learning log, not a library. Variable names, prompts and console output are in Turkish.
- API keys are read from `.env`, which is git-ignored.
