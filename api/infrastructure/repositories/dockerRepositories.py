import requests
import json
import re
import ast
import httpx

class dockerRepositorie:
    """
    Classe responsável por interagir com repositórios Docker, fornecendo funcionalidades
    para gerenciar imagens, tags, versões e operações relacionadas a repositórios.
    """
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=120
            
        )

    async def call_mcp(self, context:dict) -> str:
        """
        Envia uma requisição ao servidor MCP para gerar um Dockerfile com base no contexto fornecido.
        
        Este método:
        1. Inicializa uma sessão com o servidor MCP via JSON-RPC
        2. Armazena o ID da sessão retornado
        3. Chama a ferramenta 'generate_dockerfile' com o contexto fornecido
        4. Retorna o código gerado a partir da resposta
        
        Parâmetros:
            context (dict): Dados de contexto necessários para a geração do Dockerfile
        
        Retorna:
            str: Código gerado pelo servidor MCP
        
        Raises:
            Requisições podem levantar exceções de rede conforme documentação da biblioteca requests
        """
        
        MCP_URL = "http://mcp-server:9000/mcp"

        HEADERS = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        # # Inicializa a sessão com o servidor MCP
        # init = self.client.post(MCP_URL, json={
        #     "jsonrpc": "2.0",
        #     "id": 1,
        #     "method": "initialize",
        #     "params": {
        #         "protocolVersion": "2024-11-05",
        #         "capabilities": {},
        #         "clientInfo": {
        #             "name": "api",
        #             "version": "1.0"
        #         }
        #     }
        # }, headers=HEADERS)

        # # Extrai o ID da sessão da resposta de inicialização
        # session_id = init.headers.get("mcp-session-id")
        
        # Chama a ferramenta de geração de Dockerfile com o contexto fornecido
        resp = await self.client.post(
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
            headers=HEADERS
        )
        result = json.loads(resp.text)
        result = result.get('result').get('content')[0].get('text')
        return self.sanitize_response(result)

    async def call_mcp_compose(self, services:list) -> str:
        """Realiza uma chamada ao MCP para gerar um compose com base nos serviços fornecidos.

        Args:
            services (list): Lista de serviços a serem incluídos no compose.

        Returns:
            str: Código gerado pelo MCP após a chamada do tool generate_compose.

        Raises:
            Possíveis exceções da biblioteca requests em caso de falha nas requisições.
        """
        
        # URL base do serviço MCP
        MCP_URL = "http://mcp-server:9000/mcp"

        # Cabeçalhos comuns para as requisições
        HEADERS = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        # # Inicializa a sessão com o MCP
        # init = requests.post(MCP_URL, json={
        #     "jsonrpc": "2.0",
        #     "id": 1,
        #     "method": "initialize",
        #     "params": {
        #         "protocolVersion": "2024-11-05",
        #         "capabilities": {},
        #         "clientInfo": {
        #             "name": "api",
        #             "version": "1.0"
        #         }
        #     }
        # }, headers=HEADERS)

        # # Extrai o ID da sessão da resposta de inicialização
        # session_id = init.headers.get("mcp-session-id")
        
        # Chama o tool generate_compose com os serviços especificados
        resp = await self.client.post(
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
            headers=HEADERS
        )
        result = json.loads(resp.text)
        result = result.get('result').get('content')[0].get('text')
        return self.sanitize_response(result)

    def extrair_codigo(self, resp_text):
            """
            Extrai o conteúdo de código de uma resposta de texto, geralmente proveniente de uma API.

            A função filtra as linhas que começam com "data:", junta-as, faz o parse do JSON,
            e extrai o conteúdo de blocos de código delimitados por . Se não houver blocos,
            remove as marcações e retorna o texto limpo.

            Args:
                resp_text (str): Texto bruto da resposta, geralmente contendo dados em formato JSON
                                e possivelmente blocos de código.

            Returns:
                str: Conteúdo do código extraído e limpo, ou uma string vazia se não for possível
                    extrair ou se ocorrer um erro.
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
        """
        Sanitiza o texto de resposta removendo blocos específicos de marcação.
        
        Este método processa o texto para:
        1. Remover blocos delimitados por 'lido' e 'elid' (incluindo suas variantes)
        2. Remover trechos que contenham apenas a marca de abertura 'lido'
        3. Retornar o texto resultante com espaços em branco removidos
        
        Args:
            text (str): Texto a ser sanitizado
            
        Returns:
            str: Texto processado com as marcações removidas
        """
        # Remove blocos  lido...elid (incluindo variantes com acentos)
        # Utiliza expressão regular não-greedy (.*?) para capturar o menor bloco possível
        text = re.sub(r"lido.*?elid", "", text, flags=re.DOTALL)

        # Remove casos onde apenas a marca de abertura foi encontrada
        # (pode ocorrer em respostas truncadas ou mal formadas)
        text = re.sub(r"lido.*", "", text, flags=re.DOTALL)
        
        # remove blocos <think>...</think>
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # remove caso venha só abertura
        text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)

        return text.strip()

    def extrair_blocos(self, code: str):
        """
        Extrai blocos de código (classes e funções) de uma string de código Python.

        Args:
            code (str): Código Python a ser analisado.

        Returns:
            list: Lista de dicionários representando blocos de código. Cada dicionário contém:
                - type (str): Tipo do bloco ('class' ou 'function').
                - code (str): Código fonte do bloco.
                - methods (list, opcional): Lista de métodos para blocos do tipo 'class'.

        Raises:
            SyntaxError: Se o código fornecido contiver sintaxe inválida.
        """
        tree = ast.parse(code)
        blocks = []

        for node in tree.body:
            # Processa definições de classe
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

            # Processa funções independentes
            elif isinstance(node, ast.FunctionDef):
                func_code = ast.get_source_segment(code, node)

                blocks.append({
                    "type": "function",
                    "code": func_code
                })

        return blocks

    async def processar_codigo(self, code: str, language: str) -> str:
        """Processa o código fonte conforme a linguagem especificada.

        Para Python, utiliza análise de AST para extrair classes e funções. 
        Para outras linguagens, utiliza o MCP diretamente.

        Args:
            code (str): Código fonte a ser processado.
            language (str): Linguagem de programação do código.

        Returns:
            str: Código processado com docstrings e comentários adicionados.
        """
        print(code)  # Debug: Exibe o código recebido

        # 🔥 FIX 2: AST só para Python
        if language.lower() != "python":
            result = await self.call_mcp(code, language)
            return result  # Para linguagens não-Python, processa diretamente com MCP

        # Python usa AST
        try:
            blocks = self.extrair_blocos(code)
        except SyntaxError:
            # fallback se código vier quebrado
            result = await self.call_mcp(code, language)
            return  result # Tenta processar código com erro de sintaxe

        result_parts = []

        for block in blocks:

            if block["type"] == "class":
                class_result = await self.call_mcp(block["code"], language)
                result_parts.append(class_result)  # Processa classes individualmente

            elif block["type"] == "function":
                func_result = await self.call_mcp(block["code"], language)
                result_parts.append(func_result)  # Processa funções individualmente

        return "\n\n".join(result_parts)  # Junta os resultados com espaçamento duplo