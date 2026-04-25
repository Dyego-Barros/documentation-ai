from fastmcp import FastMCP
from agent import gerar_docstring

mcp = FastMCP("docstring-agent")

@mcp.tool()
def add_docstring(code: str) -> str:
    return gerar_docstring(code)

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=3000
    )