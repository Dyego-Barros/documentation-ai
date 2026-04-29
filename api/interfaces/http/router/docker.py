from fastapi  import APIRouter
from pydantic import BaseModel
from infrastructure.repositories.dockerRepositories import dockerRepositorie

docker= dockerRepositorie()

class dockerModel(BaseModel):
    project_type: str
    framework: str | None
    files: dict
    
class composeModel(BaseModel):
    services: list[dict]
    
dockerRouter = APIRouter(prefix="/generate", tags=["Generate"])


@dockerRouter.post(path="/dockerfile")
def generateDockerFile(req: dockerModel):
    try:
        
        dados = docker.call_mcp(context=req.model_dump())
        return dados
        
    except Exception as e:
        return {"error": str(e)}
    
@dockerRouter.post(path="/compose")
def generateCompose(req:composeModel):
    try:
        
        dados = docker.call_mcp_compose(services=req.model_dump())
        print(dados)
        return dados
    except Exception as e:
        return {"error": str(e)}