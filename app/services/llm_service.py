import os
import json

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
    If the user seems to want to book an interview, politely ask for their name, email, date, and time.

Context:
{context}

Conversation history:
{history_text}

Question: {question}

Answer using the context and conversation history. Use the conversation history to understand follow-up questions. If the answer cannot be determined from either the context or conversation history, say you don't know. """

    response = model.generate_content(prompt)
    return response.text


def extract_booking_info(
    chat_history: list[dict[str, str]],
    latest_message: str,
) -> dict:
    """Ask the LLM to extract booking details from the conversation."""

    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in chat_history
    )

    prompt = f"""Look at this conversation and determine if the user has provided ALL FOUR of: name, email, interview date, interview time.

Conversation so far:
{history_text}
user: {latest_message}

Reply with ONLY raw JSON, no markdown, no explanation.
If any of the four fields is missing or unclear, reply exactly:
{{"complete": false}}

If all four are clearly present, reply exactly:
{{"complete": true, "name": "...", "email": "...", "date": "...", "time": "..."}}"""

    raw = model.generate_content(prompt).text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except Exception:
        return {"complete": False}