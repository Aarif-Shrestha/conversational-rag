from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="File name is missing",
        )

    allowed_extensions = {".pdf", ".txt"}

    file_extension = "." + file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed",
        )

    return {
        "filename": file.filename,
        "message": "File received successfully",
    }