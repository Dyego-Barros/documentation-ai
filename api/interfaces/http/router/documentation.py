from fastapi import APIRouter
from pydantic import BaseModel
from infrastructure.repositories.documentatioRepositorie import documentationPython
from typing import Literal

doc = documentationPython()

class DocRequest(BaseModel):
    """
    Modelo de dados para requisições de geração de documentação.
    
    Attributes:
        code (str): Código-fonte que será analisado e documentado.
        language (Literal): Linguagem de programação do código fornecido.
    """
    code: str
    language: Literal["python", "javascript", "java", "csharp", "go"]

docPythonrouter = APIRouter(prefix="/languages", tags=["Documentation"])


@docPythonrouter.post(path="/docs")
def docPython(req: DocRequest):
    """
    Endpoint para processar código-fonte e gerar documentação.
    
    Este endpoint recebe um objeto com o código-fonte e a linguagem de programação,
    e retorna a documentação gerada com base no código fornecido.
    
    Args:
        req (DocRequest): Objeto contendo o código-fonte e a linguagem.
        
    Returns:
        dict: Dicionário contendo o resultado da documentação ou uma mensagem de erro.
    """
    try:
        language = req.language.lower()
        
        result = doc.processar_codigo(req.code,language)
        print(result)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}