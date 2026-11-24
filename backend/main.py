from pathlib import Path
from uuid import UUID, uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile

from groq import APIError

from groq_service import analyze_requirements


app = FastAPI(title="ManagerPilot API")

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/requirements/upload")
async def upload_requirements(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Please upload a TXT file.")

    content = await file.read(1_000_001)

    if len(content) > 1_000_000:
        raise HTTPException(status_code=413, detail="File is too large.")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The file must contain UTF-8 text.",
        )

    UPLOAD_DIR.mkdir(exist_ok=True)

    file_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{file_id}.txt"
    file_path.write_bytes(content)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "text": text,
    }

@app.post("/api/requirements/{file_id}/analyze")
def analyze_uploaded_requirements(file_id: UUID):
    file_path = UPLOAD_DIR / f"{file_id}.txt"

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    text = file_path.read_text(encoding="utf-8")

    try:
        analysis = analyze_requirements(text)
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Groq API key is not configured.",
        )
    except APIError:
        raise HTTPException(
            status_code=502,
            detail="Could not get a response from Groq.",
        )

    return {"file_id": str(file_id), "analysis": analysis}    