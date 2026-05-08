from fastmcp import FastMCP
from agent import *
from pydantic import BaseModel
import asyncio


mcp = FastMCP("docstring-agent")

app = mcp.http_app(
    path="/mcp",
    json_response=True,
    stateless_http=True,
    transport="http"
)

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
   
async def run_in_thread(func,*args): 
    return asyncio.to_thread(func, *args)
    
@mcp.tool()
async def add_docstring(code: str,language:str) -> str:
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
        "python": gerar_docstring_Python,
        "csharp": gerar_docstring_csharp,
        "java": gerar_docstring_java,
        "javascript": gerar_docstring_javascript,
        "go": gerar_docstring_go,
    }

    if language not in funcs:
        raise ValueError("Linguagem não suportada")
    result = await funcs[language](code)
    print(result)
    return result

@mcp.tool()
async def generate_dockerfile(context:dict)->str:
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
        if context!= None:
            
            response = await gerar_dockerfile(context)
            print(f"Resposta da IA: {response}")
            return response
    except Exception as e:
        print(f"Erro ao gerar dockerfile :{e}")
        
@mcp.tool()
async def generate_compose(services:list)->str:
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
        if services!= None:
            
            response = await gerar_compose(services)
            print(f"Resposta da IA: {response}")
            return response
    except Exception as e:
        print(f"Erro ao gerar dockerfile :{e}")

if __name__ == "__main__":
    import uvicorn as uv
    uv.run(
        "server:app",
        host="0.0.0.0",
        port=9000,
        reload=False,
        workers=2
    )
   