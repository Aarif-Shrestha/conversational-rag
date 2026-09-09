import json

import redis


REDIS_HOST = "127.0.0.1"
REDIS_PORT = 9000
MAX_HISTORY_MESSAGES = 10

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


def _session_key(session_id: str) -> str:
    return f"chat:{session_id}"


def get_history(session_id: str) -> list[dict[str, str]]:
    """Retrieve chat history for a session."""

    raw_history = redis_client.get(_session_key(session_id))

    if raw_history is None:
        return []

    return json.loads(raw_history)


def add_message(
    session_id: str,
    role: str,
    content: str,
) -> None:
    """Append a message to a session's chat history."""

    history = get_history(session_id)

    history.append({
        "role": role,
        "content": content,
    })

    # Keep only the most recent messages to avoid unbounded growth
    history = history[-MAX_HISTORY_MESSAGES:]

    redis_client.set(
        _session_key(session_id),
        json.dumps(history),
    )