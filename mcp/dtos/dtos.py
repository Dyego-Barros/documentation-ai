from pydantic import BaseModel
from typing import Literal

class dockerModel(BaseModel):
    """
    Modelo Pydantic que representa a estrutura de dados para geração de Dockerfile.
    
    Attributes:
        project_type (str): Tipo do projeto (ex: web, backend, etc).
        framework (str | None): Framework utilizado no projeto.
        files (dict): Estrutura de arquivos do projeto.
    """
    project_type: str
    framework: str | None
    files: dict
    
class RequestModel(BaseModel):
    """
    Modelo Pydantic para requisições de geração de Dockerfile.
    
    Attributes:
        context (dict): Dados de contexto necessários para a geração do Dockerfile.
    """
    code:str
    language: Literal["python", "javascript", "java", "csharp", "go"]
    
    
class composeModel(BaseModel):
    """
    Modelo para definir serviços em um Docker Compose.
    
    Attributes:
        services: Lista de serviços a serem incluídos no compose
    """
    services: list[dict]