from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="ManagerPilot API")


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

    return {"filename": file.filename, "text": text}