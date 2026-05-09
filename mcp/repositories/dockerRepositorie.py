import requests
import json
import re
import ast
import httpx
from agents.agent import Agent


class DockerRepositorie:
    """
    Classe responsável por interagir com repositórios Docker, fornecendo funcionalidades
    para gerenciar imagens, tags, versões e operações relacionadas a repositórios.
    """
    def __init__(self):
        self.agent = Agent()  # Instância do agente para chamadas ao MCP

    async def __call_agent_dockerfile(self, context:dict) -> str:
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
        
        # MCP_URL = "http://mcp-server:9000/mcp"

        # HEADERS = {
        #     "Accept": "application/json, text/event-stream",
        #     "Content-Type": "application/json"
        # }
        
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
        # resp = await self.client.post(
        #     MCP_URL,
        #     json={
        #         "jsonrpc": "2.0",
        #         "id": 2,
        #         "method": "tools/call",
        #         "params": {
        #             "name": "generate_dockerfile",
        #             "arguments":{
        #                 "context":context
        #                 } 
        #         }
        #     },
        #     headers=HEADERS
        # )
        resp = await self.agent.gerar_dockerfile(context)
        result = json.loads(resp.text)
        result = result.get('result').get('content')[0].get('text')
        return self.sanitize_response(result)

    async def __call_agent_dockercompose(self, services:list) -> str:
        """Realiza uma chamada ao MCP para gerar um compose com base nos serviços fornecidos.

        Args:
            services (list): Lista de serviços a serem incluídos no compose.

        Returns:
            str: Código gerado pelo MCP após a chamada do tool generate_compose.

        Raises:
            Possíveis exceções da biblioteca requests em caso de falha nas requisições.
        """
        
        # URL base do serviço MCP
        # MCP_URL = "http://mcp-server:9000/mcp"

        # # Cabeçalhos comuns para as requisições
        # HEADERS = {
        #     "Accept": "application/json, text/event-stream",
        #     "Content-Type": "application/json"
        # }
        
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
        # resp = await self.client.post(
        #     MCP_URL,
        #     json={
        #         "jsonrpc": "2.0",
        #         "id": 2,
        #         "method": "tools/call",
        #         "params": {
        #             "name": "generate_compose",
        #             "arguments": services
        #         }
        #     },
        #     headers=HEADERS
        # )
        resp = await self.call_agent_dockercompose(services)
        result = json.loads(resp.text)
        result = result.get('result').get('content')[0].get('text')
        return self.__sanitize_response(result)

    

    def __sanitize_response(self, text: str) -> str:
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
        text = text.replace("dockerfile","")
        text = text.replace("compose","")
        text = text.replace("docker-compose","")
        text = text.replace("```","")

        return text.strip()

    
    async def processar_codigo(self, code: dict | list) -> str:
        """Processa o código fonte conforme a linguagem especificada.

        Para Python, utiliza análise de AST para extrair classes e funções. 
        Para outras linguagens, utiliza o MCP diretamente.

        Args:
            code (str): Código fonte a ser processado.
            language (str): Linguagem de programação do código.

        Returns:
            str: Código processado com docstrings e comentários adicionados.
        """
        
        try:
            if isinstance(code, dict):
                result = await self.__call_agent_dockerfile(code)
                return result
                source_code = code.get("code")
            elif isinstance(code,list):
                result = await self.__call_agent_dockercompose(code)
                return result
        except Exception as e:
            print(f"Erro ao processar código: {e}")
            return ""