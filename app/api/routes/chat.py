from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.booking import Booking
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embedding_service import generate_embedding
from app.services.vector_service import search_similar_chunks
from app.services.memory_service import get_history, add_message
from app.services.llm_service import generate_answer, extract_booking_info

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    query_embedding = generate_embedding(request.message)
    context_chunks = search_similar_chunks(query_embedding)
    history = get_history(request.session_id)

    booking_info = extract_booking_info(history, request.message)

    if booking_info.get("complete"):
        record = Booking(
            session_id=request.session_id,
            name=booking_info["name"],
            email=booking_info["email"],
            date=booking_info["date"],
            time=booking_info["time"],
        )
        db.add(record)
        db.commit()

        answer = (
            f"Your interview is booked for {booking_info['date']} "
            f"at {booking_info['time']}. Confirmation sent to {booking_info['email']}."
        )
    else:
        answer = generate_answer(request.message, context_chunks, history)

    add_message(request.session_id, "user", request.message)
    add_message(request.session_id, "assistant", answer)

    return ChatResponse(session_id=request.session_id, answer=answer)