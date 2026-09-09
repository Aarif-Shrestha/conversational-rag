from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embedding_service import generate_embedding
from app.services.vector_service import search_similar_chunks
from app.services.memory_service import get_history, add_message
from app.services.llm_service import generate_answer


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    query_embedding = generate_embedding(request.message)

    context_chunks = search_similar_chunks(query_embedding)

    history = get_history(request.session_id)

    answer = generate_answer(
        question=request.message,
        context_chunks=context_chunks,
        chat_history=history,
    )

    add_message(request.session_id, "user", request.message)
    add_message(request.session_id, "assistant", answer)

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
    )