from fastapi import APIRouter
from pydantic import BaseModel
from infrastructure.repositories.dockerRepositories import dockerRepositorie

docker = dockerRepositorie()

class dockerModel(BaseModel):
    """
    Modelo para dados necessários para gerar um Dockerfile.
    
    Attributes:
        project_type: Tipo do projeto (ex: python, node, etc)
        framework: Framework utilizado (opcional)
        files: Estrutura de arquivos do projeto
    """
    project_type: str
    framework: str | None
    files: dict
    
class composeModel(BaseModel):
    """
    Modelo para definir serviços em um Docker Compose.
    
    Attributes:
        services: Lista de serviços a serem incluídos no compose
    """
    services: list[dict]
    
dockerRouter = APIRouter(prefix="/generate", tags=["Generate"])

@dockerRouter.post(path="/dockerfile")
def generateDockerFile(req: dockerModel):
    """
    Gera um Dockerfile com base nos parâmetros fornecidos.
    
    Args:
        req: Modelo contendo os dados do projeto
        
    Returns:
        Conteúdo do Dockerfile gerado ou mensagem de erro
    """
    try:
        # Chama o repositório para gerar o Dockerfile
        dados = docker.call_mcp(context=req.model_dump())
        return dados
        
    except Exception as e:
        # Retorna mensagem de erro em caso de falha
        return {"error": str(e)}
    
@dockerRouter.post(path="/compose")
def generateCompose(req:composeModel):
    """
    Gera um arquivo docker-compose.yml com base nos serviços fornecidos.
    
    Args:
        req: Modelo contendo a definição dos serviços
        
    Returns:
        Conteúdo do compose gerado ou mensagem de erro
    """
    try:
        # Chama o repositório para gerar o Docker Compose
        dados = docker.call_mcp_compose(services=req.model_dump())
        return dados
        
    except Exception as e:
        # Retorna mensagem de erro em caso de falha
        return {"error": str(e)}