from fastapi import APIRouter
from pydantic import BaseModel
from infrastructure.repositories.documentatioRepositorie import documentationPython
from typing import Literal

doc = documentationPython()

class DocRequest(BaseModel):
    code: str
    language: Literal["python", "javascript", "java", "csharp", "go"]

docPythonrouter = APIRouter(prefix="/languages", tags=["Documentation"])


@docPythonrouter.post(path="/docs")
def docPython(req: DocRequest):
    try:
        language = req.language.lower()
        
        result = doc.processar_codigo(req.code,language)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
    
