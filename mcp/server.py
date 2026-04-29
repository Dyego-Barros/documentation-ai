from fastmcp import FastMCP
from agent import *
from pydantic import BaseModel
mcp = FastMCP("docstring-agent")

class dockerModel(BaseModel):
    project_type: str
    framework: str | None
    files: dict
    
    
@mcp.tool()
def add_docstring(code: str,language:str) -> str:
    
    funcs = {
        "python": gerar_docstring_Python,
        "csharp": gerar_docstring_csharp,
        "java": gerar_docstring_java,
        "javascript": gerar_docstring_javascript,
        "go": gerar_docstring_go,
    }

    if language not in funcs:
        raise ValueError("Linguagem não suportada")
    return funcs[language](code)

@mcp.tool()
def generate_dockerfile(context:dict)->str:
    try:
        if context!= None:
            
            response = gerar_dockerfile(context=context)
            return response
    except Exception as e:
        print(f"Erro ao gerar dockerfile :{e}")
        
@mcp.tool()
def generate_compose(services:list)->str:
    try:
        if services!= None:
            
            response = gerar_compose(services=services)
            return response
    except Exception as e:
        print(f"Erro ao gerar dockerfile :{e}")

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=9000
    )