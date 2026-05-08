import requests
import json
import re
import ast

class dockerRepositorie:
    """
    Classe responsável por interagir com repositórios Docker, fornecendo funcionalidades para gerenciar imagens, tags e registros.
    Utiliza a biblioteca requests para fazer requisições HTTP, json para processar dados em formato JSON, re para validação de padrões e ast para análise de estruturas de dados.
    """
    pass

def call_mcp(self, context:dict) -> str:
    """
    Chama o MCP (Model Control Protocol) para gerar um Dockerfile com base no contexto fornecido.

    Este método envia uma requisição POST para inicializar a sessão com o servidor MCP,
    obtém o ID da sessão e, em seguida, chama a ferramenta 'generate_dockerfile' com o contexto
    fornecido como parâmetro.

    Args:
        context (dict): Dicionário contendo o contexto necessário para a geração do Dockerfile.

    Returns:
        str: Código gerado retornado pela resposta do servidor MCP.
    """

    MCP_URL = "http://mcp-server:9000/mcp"

    HEADERS = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    # Inicializa a sessão com o servidor MCP
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

    # Extrai o ID da sessão da resposta de inicialização
    session_id = init.headers.get("mcp-session-id")
    
    # Chama a ferramenta 'generate_dockerfile' com o contexto fornecido
    resp = requests.post(
        MCP_URL,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "generate_dockerfile",
                "arguments":{
                    "context":context
                    } 
            }
        },
        headers={**HEADERS, "mcp-session-id": session_id},
        timeout=360
    )
    # Extrai e retorna o código gerado da resposta
    return self.extrair_codigo(resp.text)

def call_mcp_compose(self, services:list) -> str:
    """
    Chama o serviço MCP para gerar um arquivo compose.yaml com base nos serviços fornecidos.

    Args:
        services (list): Lista de serviços que serão utilizados para gerar o compose.

    Returns:
        str: Conteúdo do arquivo compose.yaml gerado, extraído da resposta da API.

    Raises:
        Pode levantar exceções relacionadas a falhas de rede ou resposta inválida da API MCP.
    """
    
    MCP_URL = "http://mcp-server:9000/mcp"

    HEADERS = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    # Inicializa a sessão com o servidor MCP
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

    # Extrai o ID da sessão da resposta de inicialização
    session_id = init.headers.get("mcp-session-id")
    
    # Chama a ferramenta 'generate_compose' no servidor MCP para gerar o compose.yaml
    resp = requests.post(
        MCP_URL,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "generate_compose",
                "arguments": services
            }
        },
        headers={**HEADERS, "mcp-session-id": session_id},
        timeout=360
    )
    # Extrai o conteúdo do compose.yaml da resposta e retorna
    return self.extrair_codigo(resp.text)

def extrair_codigo(self, resp_text):
    """Extrai e sanitiza blocos de código de uma resposta de texto contendo dados em formato 'JSON'.

    Args:
        resp_text (str): Texto de resposta contendo linhas no formato '{json}' e possíveis blocos de código.

    Returns:
        str: Conteúdo do código extraído e sanitizado, ou string vazia se não houver código válido.
    """
    data_lines = []

    # Junta apenas as linhas que começam com "data:"
    for line in resp_text.splitlines():
        if line.startswith("data:"):
            data_lines.append(line[len("data:"):].strip())

    if not data_lines:
        return ""

    # Junta e faz parse do JSON
    full_data = "".join(data_lines)

    try:
        parsed = json.loads(full_data)
        text = parsed["result"]["content"][0]["text"]
    except (json.JSONDecodeError, KeyError, IndexError):
        return ""

    # Extrai apenas o conteúdo dentro de blocos  (mais seguro)
    code_blocks = re.findall(r"(?:\w+)?\s*([\s\S]*?)", text)

    if code_blocks:
        # Junta múltiplos blocos, se existirem
        text = "\n\n".join(code_blocks)
    else:
        # fallback: remove marcações soltas
        text = re.sub(r"[\w]*\n?", "", text)
        text = re.sub(r"", "", text)

    # Corrige encoding (se necessário)
    try:
        text = text.encode("latin1").decode("utf-8")
        text = self.sanitize_response(text=text)
    except Exception:
        pass

    return text.strip()

def sanitize_response(self, text: str) -> str:
    """Remove blocos de texto entre 'lido' e 'end' e casos de abertura sem fechamento.

    Args:
        text (str): Texto a ser sanitizado.

    Returns:
        str: Texto processado com os blocos removidos e espaços em branco removidos.
    """
    # remove blocos lido...end
    text = re.sub(r"lido.*?end", "", text, flags=re.DOTALL)

    # remove caso venha só abertura
    text = re.sub(r"lido.*", "", text, flags=re.DOTALL)

    return text.strip()

def extrair_blocos(self, code: str):
    """Extrai blocos de código correspondentes a classes e funções do código fonte fornecido.

    Args:
        code (str): Código Python a ser analisado.

    Returns:
        list: Lista de dicionários contendo informações sobre cada bloco extraído.
              Cada dicionário tem as chaves 'type' (class/function), 'code' (código do bloco),
              e 'methods' (lista de métodos, apenas para classes).
    """
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

def processar_codigo(self, code: str, language: str) -> str:
    """
    Processa o código fonte de acordo com a linguagem especificada.

    Para código em Python, utiliza análise de AST para extrair classes e funções
    e processá-las individualmente. Para outras linguagens, utiliza fallback
    para o método call_mcp.

    Args:
        code (str): Código fonte a ser processado.
        language (str): Linguagem do código (ex: 'python', 'javascript', etc.).

    Returns:
        str: Código processado com as modificações aplicadas.
    """

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