import requests
import json
import re
import ast

class documentationPython:
    # -----------------------------
    # MCP CALL (sem mudança)
    # -----------------------------
    def call_mcp(self, code: str, language: str) -> str:
        
        MCP_URL = "http://mcp-server:9000/mcp"

        HEADERS = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
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
                    "arguments": {"code": code, "language": language}
                }
            },
            headers={**HEADERS, "mcp-session-id": session_id}
        )

        return self.extrair_codigo(resp.text)


    # -----------------------------
    # RESPONSE PARSER (limpo)
    # -----------------------------
    def extrair_codigo(self, resp_text):
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
            text = self.sanitize_response(text=text)
        except:
            pass

        return text.strip()

    def sanitize_response(self,text: str) -> str:
        # remove blocos <think>...</think>
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # remove caso venha só abertura
        text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)

        return text.strip()
    # -----------------------------
    # AST PARSER (com FIX 2 🔥)
    # -----------------------------
    def extrair_blocos(self, code: str):
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
    # PROCESSAMENTO INTELIGENTE (FIX 2 AQUI 🔥)
    # -----------------------------
    def processar_codigo(self, code: str, language: str) -> str:

        print(code)

        # 🔥 FIX 2: AST só para Python
        if language.lower() != "python":
            result = self.call_mcp(code, language)
            return result

        # Python usa AST
        try:
            blocks = self.extrair_blocos(code)
        except SyntaxError:
            # fallback se código vier quebrado
            return self.call_mcp(code, language)

        result_parts = []

        for block in blocks:

            if block["type"] == "class":
                class_result = self.call_mcp(block["code"], language)
                result_parts.append(class_result)

            elif block["type"] == "function":
                func_result = self.call_mcp(block["code"], language)
                result_parts.append(func_result)

        return "\n\n".join(result_parts)