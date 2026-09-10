from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.services.document_service import extract_text, chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.vector_service import create_collection, store_chunks



router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: str = "recursive",
    db: Session = Depends(get_db),
):
    # 1. Check filename
    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="File name is missing",
        )

    # 2. Check file type
    allowed_extensions = {".pdf", ".txt"}

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed",
        )

    # 3. Create unique document ID
    document_id = str(uuid4())

    # 4. Create file path
    file_path = UPLOAD_DIR / f"{document_id}{file_extension}"

    # 5. Read uploaded file
    file_content = await file.read()

    # 6. Save file
    file_path.write_bytes(file_content)

    # 7. Extract text
    try:
        text = extract_text(str(file_path))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text: {error}",
        )

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the document",
        )

    # 8. Split text into chunks
    try:
        chunks = chunk_text(
            text=text,
            strategy=chunking_strategy,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    # 9. Generate embeddings
    embeddings = generate_embeddings(chunks)

    # 10. Create Qdrant collection
    create_collection()

    # 11. Store chunks + embeddings in Qdrant
    store_chunks(
        document_id=document_id,
        filename=file.filename,
        chunks=chunks,
        embeddings=embeddings,
    )

    document_record = Document(
        document_id=document_id,
        filename=file.filename,
        file_type=file_extension,
        chunking_strategy=chunking_strategy,
        chunk_count=len(chunks),
    )
    db.add(document_record)
    db.commit()

    # 12. Return result
    return {
        "document_id": document_id,
        "filename": file.filename,
        "file_type": file_extension,
        "chunking_strategy": chunking_strategy,
        "text_length": len(text),
        "chunk_count": len(chunks),
        "message": "Document uploaded and stored successfully",
    }
   