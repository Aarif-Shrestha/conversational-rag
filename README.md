# Conversational RAG Chatbot

A backend system with two REST APIs built using **FastAPI**:

1. **Document Ingestion API** — upload PDF/TXT files, extract text, chunk it (two selectable strategies), generate embeddings, and store them in Qdrant with metadata saved in PostgreSQL.
2. **Conversational RAG API** — a custom Retrieval-Augmented Generation pipeline (no `RetrievalQAChain`) with Redis-based multi-turn chat memory and LLM-driven interview booking.

---

## Tech Stack

- **FastAPI** — REST API framework
- **Qdrant** — vector database (embeddings storage & similarity search)
- **PostgreSQL** — relational database (document metadata & interview bookings)
- **Redis** — chat memory store (multi-turn conversation history)
- **SQLAlchemy** — ORM for PostgreSQL
- **Sentence-Transformers (`all-MiniLM-L6-v2`)** — embedding generation (384-dim vectors)
- **Google Gemini API** — LLM for answer generation and booking extraction
- **Docker** — used to run Qdrant, PostgreSQL, and Redis locally

---

## Prerequisites

- Python 3.12
- Docker installed and running
- A free [Gemini API key](https://aistudio.google.com/apikey)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd conversational-rag
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Start required services with Docker

**Qdrant (vector database):**

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

**PostgreSQL (metadata & bookings):**

```bash
docker run -d --name postgres-rag \
  -e POSTGRES_USER=raguser \
  -e POSTGRES_PASSWORD=ragpass \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  postgres:16
```

**Redis (chat memory):**

```bash
docker run -d --name redis-rag -p 6379:6379 redis:7
```

This both creates and starts the container in one step (`-d` runs it in the background). If it already exists but is stopped, start it instead with:

```bash
docker start redis-rag
```

> If you already have a Redis container running on a different host port (e.g. `9000:6379`), you don't need a new one — just make sure `REDIS_PORT` in `app/services/memory_service.py` matches whatever host port your existing container uses.

Verify all three containers are running:

```bash
docker ps
```

You should see `qdrant`, `postgres-rag`, and `redis-rag` listed.

> **Note:** if you use different ports than the defaults above (e.g. an existing Redis container on a different port), update the host/port values in `app/core/database.py` and `app/services/memory_service.py` accordingly.

### 6. Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive API docs (Swagger UI):

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### `POST /documents/upload`

Upload a PDF or TXT file for ingestion.

**Query parameter:**
- `chunking_strategy`: `"fixed"` or `"recursive"` (default: `"recursive"`)

**Form data:**
- `file`: the PDF/TXT file to upload

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "example.txt",
  "file_type": ".txt",
  "chunking_strategy": "recursive",
  "text_length": 1720,
  "chunk_count": 5,
  "message": "Document uploaded and stored successfully"
}
```

### `POST /chat`

Send a message in a conversational RAG session. Supports multi-turn queries and interview booking.

**Request body:**
```json
{
  "session_id": "user-session-1",
  "message": "What projects has Aarif worked on?"
}
```

**Response:**
```json
{
  "session_id": "user-session-1",
  "answer": "Aarif has worked on..."
}
```

To book an interview, simply continue the conversation naturally, e.g.:

```json
{
  "session_id": "user-session-1",
  "message": "I'd like to book an interview. My name is Aarif Shrestha, email aarif@test.com, date 2026-09-15, time 3pm."
}
```

The system will detect the intent, extract the details, and store the booking in PostgreSQL.

---

## Project Structure

```
conversational-rag/
│
├── app/
│   ├── main.py                     # FastAPI app entrypoint
│   │
│   ├── api/routes/
│   │   ├── documents.py            # Document ingestion endpoint
│   │   └── chat.py                 # Conversational RAG endpoint
│   │
│   ├── services/
│   │   ├── document_service.py     # Text extraction & chunking
│   │   ├── embedding_service.py    # Embedding generation
│   │   ├── vector_service.py       # Qdrant storage & similarity search
│   │   ├── memory_service.py       # Redis chat memory
│   │   └── llm_service.py          # LLM answer generation & booking extraction
│   │
│   ├── models/
│   │   ├── document.py             # SQLAlchemy Document model
│   │   └── booking.py              # SQLAlchemy Booking model
│   │
│   ├── schemas/
│   │   └── chat.py                 # Pydantic request/response schemas
│   │
│   └── core/
│       └── database.py             # SQLAlchemy engine & session setup
│
├── uploads/                        # Uploaded files (gitignored)
├── tests/
├── .env                             # Environment variables (gitignored)
├── .gitignore
└── requirements.txt
```

---

## Design Notes

- **Two chunking strategies** are implemented: fixed-size chunking (splits text every N characters with overlap) and recursive chunking (splits along paragraph → sentence → word boundaries using LangChain's `RecursiveCharacterTextSplitter`).
- **No `RetrievalQAChain`** is used. The RAG pipeline is built manually: the user's query is embedded, relevant chunks are retrieved from Qdrant, chat history is pulled from Redis, a prompt is constructed by hand, and the result is sent directly to the Gemini API.
- **No FAISS or Chroma** — Qdrant is used exclusively as the vector store.
- **Interview booking** is handled conversationally: the LLM is used to detect booking intent and extract structured fields (name, email, date, time) from natural language, rather than requiring a separate form-based endpoint.

---

## Verifying Data

**Check Qdrant collections (dashboard):**
```
http://localhost:6333/dashboard
```

**Check PostgreSQL data:**
```bash
docker exec -it postgres-rag psql -U raguser -d ragdb -c "SELECT * FROM documents;"
docker exec -it postgres-rag psql -U raguser -d ragdb -c "SELECT * FROM bookings;"
```

**Check Redis chat history:**
```bash
docker exec -it redis-rag redis-cli
> GET chat:your-session-id
```