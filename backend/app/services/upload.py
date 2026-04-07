import os
import uuid

from fastapi import UploadFile

from app.config import settings


async def save_upload(file: UploadFile, session_id: str) -> str:
    """Save uploaded video file and return its relative path."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "video.mp4")[1] or ".mp4"
    filename = f"{session_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(settings.upload_dir, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath
