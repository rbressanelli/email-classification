from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.core.schemas import HealthResponse
from app.services.document_reader import read_document
from app.services.orchestrator import EmailAnalysisOrchestrator

router = APIRouter()
orchestrator = EmailAnalysisOrchestrator()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", provider=orchestrator.provider_name)


@router.post("/api/analyze")
async def analyze_email(
    text: str = Form(default=""),
    file: UploadFile | None = File(default=None),
):
    content = text.strip()

    if file and file.filename:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in {".txt", ".pdf"}:
            raise HTTPException(status_code=400, detail="Envie um arquivo .txt ou .pdf")

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            data = await file.read()
            tmp.write(data)
            temp_path = tmp.name

        try:
            extracted = read_document(temp_path, file.filename)
        finally:
            Path(temp_path).unlink(missing_ok=True)

        content = f"{content}\n\n{extracted}".strip()

    if not content:
        raise HTTPException(
            status_code=400, detail="Informe um texto ou envie um arquivo para análise."
        )

    return orchestrator.analyze(content)


@router.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
    <!DOCTYPE html>
    <html lang='pt-BR'>
      <head>
        <meta charset='UTF-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1.0' />
        <title>Smart Email Triage</title>
        <script>
          window.location.href = '/app';
        </script>
      </head>
      <body></body>
    </html>
    """
