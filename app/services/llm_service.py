import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_answer(
    question: str,
    context_chunks: list[str],
    chat_history: list[dict[str, str]],
) -> str:
    context = "\n\n".join(context_chunks)

    history_text = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in chat_history
    )

    prompt = f"""You are a helpful assistant answering questions based on the context below.

Context:
{context}

Conversation history:
{history_text}

Question: {question}

Answer based only on the context above. If the answer isn't in the context, say you don't know."""

    response = model.generate_content(prompt)
    return response.text