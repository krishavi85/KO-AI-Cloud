import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Document, User
from app.services.file_parser import chunk_text, parse_file
from app.services.rag import index_chunks

router = APIRouter(prefix="/files", tags=["files"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = (file.filename or "upload.bin").replace("/", "_").replace("\\", "_")
    target = Path(settings.UPLOAD_DIR) / f"u{user.id}_{safe_name}"

    data = file.file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum upload size is 25 MB.")

    with target.open("wb") as out:
        out.write(data)

    doc = Document(
        user_id=user.id,
        filename=safe_name,
        content_type=file.content_type,
        path=str(target),
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        text = parse_file(str(target), file.content_type)
        chunks = chunk_text(text)
        if not chunks:
            doc.status = "empty"
            db.commit()
            return {"document_id": doc.id, "filename": safe_name, "status": doc.status, "chunks": 0}

        indexed = index_chunks(user.id, doc.id, safe_name, chunks)
        doc.status = "indexed"
        doc.chunks = indexed
        db.commit()
        return {"document_id": doc.id, "filename": safe_name, "status": doc.status, "chunks": indexed}
    except Exception as exc:
        doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=f"File ingestion failed: {exc}") from exc


@router.get("")
def list_files(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == user.id).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "status": d.status,
            "chunks": d.chunks,
            "created_at": d.created_at,
        }
        for d in docs
    ]
