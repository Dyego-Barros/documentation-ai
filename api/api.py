from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import re
import ast

app = FastAPI()

MCP_URL = "http://localhost:3000/mcp"

HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
}


class DocRequest(BaseModel):
    code: str


# -----------------------------
# MCP CALL (sem mudança)
# -----------------------------
def call_mcp(code: str) -> str:
    init = requests.post(MCP_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "api",
                "version": "1.0"
            }
        }
    }, headers=HEADERS)

    session_id = init.headers.get("mcp-session-id")

    resp = requests.post(
        MCP_URL,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "add_docstring",
                "arguments": {"code": code}
            }
        },
        headers={**HEADERS, "mcp-session-id": session_id}
    )

    return extrair_codigo(resp.text)


# -----------------------------
# RESPONSE PARSER (limpo)
# -----------------------------
def extrair_codigo(resp_text):
    data_lines = []

    for line in resp_text.splitlines():
        if line.startswith("data:"):
            data_lines.append(line.replace("data: ", ""))

    full_data = "".join(data_lines)
    parsed = json.loads(full_data)

    text = parsed["result"]["content"][0]["text"]

    text = re.sub(r"```[\w]*\n?", "", text)
    text = re.sub(r"```", "", text)

    try:
        text = text.encode("latin1").decode("utf-8")
    except:
        pass

    return text.strip()


# -----------------------------
# AST PARSER (NOVA PARTE 🔥)
# -----------------------------
def extrair_blocos(code: str):
    tree = ast.parse(code)
    blocks = []

    for node in tree.body:
        # Classe
        if isinstance(node, ast.ClassDef):
            class_code = ast.get_source_segment(code, node)

            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_code = ast.get_source_segment(code, item)
                    methods.append(method_code)

            blocks.append({
                "type": "class",
                "code": class_code,
                "methods": methods
            })

        # Função solta
        elif isinstance(node, ast.FunctionDef):
            func_code = ast.get_source_segment(code, node)

            blocks.append({
                "type": "function",
                "code": func_code
            })

    return blocks


# -----------------------------
# PROCESSAMENTO INTELIGENTE
# -----------------------------
def processar_codigo(code: str) -> str:
    """_summary_

    Args:
        code (str): _description_

    Returns:
        str: _description_
    """
    blocks = extrair_blocos(code)

    result_parts = []

    for block in blocks:

        # Classe
        if block["type"] == "class":
            class_result = call_mcp(block["code"])
            result_parts.append(class_result)

        # Função solta
        elif block["type"] == "function":
            func_result = call_mcp(block["code"])
            result_parts.append(func_result)

    return "\n\n".join(result_parts)


# -----------------------------
# ENDPOINT
# -----------------------------
@app.post("/docstring")
def gerar_docstring(req: DocRequest):
    try:
        result = processar_codigo(req.code)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )