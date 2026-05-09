from fastmcp import FastMCP
from repositories.docRepositorie import Documentation
from repositories.dockerRepositorie import DockerRepositorie
from dtos.dtos import RequestModel, dockerModel, composeModel
from fastapi import FastAPI
from fastapi import status
from fastapi import Depends
from contextlib import asynccontextmanager


mcp = FastMCP("docstring-agent")

mcp_app = mcp.http_app(
    path="/",
    json_response=True,
    stateless_http=True,
    transport="http"
)

@asynccontextmanager
async def lifespan(app):
    async with mcp.lifespan():
        yield

app= FastAPI(title="API Tools Extension AI", lifespan=lifespan)


app.mount("/mcp", mcp_app)

def get_doc():
    return  Documentation()

def get_docker():
    return  DockerRepositorie()




    
@app.post("/languages/docs", status_code=status.HTTP_200_OK)
async def add_docstring(req:RequestModel, doc:Documentation=Depends(get_doc)) -> dict:
    """
    Adiciona docstrings a funções e métodos no código-fonte, de acordo com a linguagem especificada.

    Args:
        code (str): Código-fonte a ser processado.
        language (str): Linguagem de programação do código (ex: python, csharp, java, etc).

    Returns:
        str: Código-fonte com docstrings adicionadas.

    Raises:
        ValueError: Se a linguagem especificada não for suportada.
    """
    
    funcs = {
        "python": doc.processar_codigo,
        "csharp": doc.processar_codigo,
        "java": doc.processar_codigo,
        "javascript": doc.processar_codigo,
        "go": doc.processar_codigo,
    }
    
    language = req.language.lower()
    
    if language not in funcs:
        raise ValueError("Linguagem não suportada")
    result = await funcs[language](code=req.code,language=language)
    print(result)
    return {"result": result}

@app.post("/generate/dockerfile", status_code=status.HTTP_200_OK)
async def generate_dockerfile(req: dockerModel, docker:DockerRepositorie=Depends(get_docker))->dict:
    
    """
    Gera um Dockerfile com base no contexto fornecido.

    Args:
        context (dict): Dados de contexto para a geração do Dockerfile.

    Returns:
        str: Conteúdo do Dockerfile gerado.

    Raises:
        Exception: Se ocorrer um erro durante a geração do Dockerfile.
    """
    try:
        
            
        response = await docker.processar_codigo(code=req.model_dump())
        print(f"Resposta da IA: {response}")
        return {"result": response}
    except Exception as e:
        print(f"Erro ao gerar dockerfile :{e}")
        
@app.post("/generate/compose", status_code=status.HTTP_200_OK)
async def generate_compose(req: composeModel, docker:DockerRepositorie=Depends(get_docker))->dict:
    """
    Gera um arquivo docker-compose.yml com base na lista de serviços fornecida.

    Args:
        services (list): Lista de serviços para compor o docker-compose.

    Returns:
        str: Conteúdo do arquivo docker-compose.yml gerado.

    Raises:
        Exception: Se ocorrer um erro durante a geração do docker-compose.
    """
    try:
        if len(req.services) > 0:
            response = await docker.processar_codigo(code=req.services)
            print(f"Resposta da IA: {response}")
            return {"result": response}
    except Exception as e:
        print(f"Erro ao gerar dockerfile :{e}")

if __name__ == "__main__":
    import uvicorn as uv
    uv.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
        
       
    )
   