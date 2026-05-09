import requests
import json
import re
import ast
import httpx
from agents.agent import Agent


class Documentation:
    """Classe base para geração de documentação.
    
    Responsável por adicionar docstrings e comentários
    seguindo as diretrizes PEP 257. Utilizada por engenheiros
    de software senior para documentação de código.
    """
    
    def __init__(self):
        """Inicializa uma instância da classe com um cliente HTTP assíncrono.
        
        O cliente é configurado com um tempo limite de 120 segundos para requisições assíncronas.
        """
        self.agent = Agent()  # Instância do agente para chamadas ao MCP

        
    async def __call_agent(self, code: str, language: str) -> str:
        """
        Call the MCP API to add a docstring to the given code.

        Parameters:
        code (str): The code to add a docstring to.
        language (str): The language of the code.

        Returns:
        str: The sanitized response from the API.

        """
        functions = {
            "python": self.agent.gerar_docstring_Python,
            "csharp": self.agent.gerar_docstring_csharp,
            "java": self.agent.gerar_docstring_java,
            "javascript": self.agent.gerar_docstring_javascript,
            "go": self.agent.gerar_docstring_go
        }
        result = await functions[language](code)
        # result = json.loads(resp.text)
        # result = result.get('result').get('content')[0].get('text')
        print(f"Resposta bruta da IA: {result}")
        return self.__sanitize_response(result)
    


    # -----------------------------
    # RESPONSE PARSER (limpo)
    # -----------------------------
    

    def __extrair_codigo(self, resp_text):
        """
    Extrai o texto de uma resposta JSON que contém dados em formato de código.

    Args:
        resp_text (str): Texto da resposta JSON.

    Returns:
        str: Texto limpo e formatado.
    """
        data_lines = []
        for line in resp_text.splitlines():
            if line.startswith('data:'):
                data_lines.append(line.replace('data: ', ''))
        full_data = ''.join(data_lines)
        parsed = json.loads(full_data)
        text = parsed['result']['content'][0]['text']
        text = re.sub('[\\w]*\\n?', '', text)
        text = re.sub('', '', text)
        try:
            text = text.encode('latin1').decode('utf-8')
            text = self.sanitize_response(text=text)
        except:
            pass
        return text.strip()

    def __sanitize_response(self, text: str) -> str:
        """
        Limpa a resposta da IA removendo tags de pensamento, delimitadores de markdown
        e rótulos de linguagem soltos no texto.
        """
        # 1. Remove blocos de pensamento <think>...</think> completos ou incompletos
        text = re.sub(r"<think>.*?(?:</think>|\$)", "", text, flags=re.DOTALL)

        # 2. Remove blocos de código Markdown completos (ex: ```javascript ... ```)
        # Pegamos o que está dentro das crases triplas
        text = re.sub(r"```(?:\w+)?\n?(.*?)```", r"\1", text, flags=re.DOTALL)

        # 3. Remove rótulos de linguagem soltos no início ou meio do texto (como 'javascript' puro)
        # Isso limpa palavras como 'javascript' ou 'python' que aparecem sozinhas em uma linha
        languages = ['javascript', 'python', 'typescript', 'java', 'csharp', 'go']
        for lang in languages:
            # Remove a palavra se ela estiver sozinha em uma linha (comum em falhas de geração)
            text = re.sub(rf"^\s*{lang}\s*\$", "", text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(rf"```{lang}(?:\w+)?\n?(.*?)```", r"\1", text, flags=re.MULTILINE | re.DOTALL)
            text = text.replace(f"```{lang}", "")


        # 4. Limpeza final de crases triplas remanescentes e espaços inúteis
        text = text.replace("```", "")
        
        return text.strip()
        
    def __formatar_codigo(self, code: list) -> str:
        """
        Formata uma lista de strings (linhas de código) aplicando uma indentação 
        base àquilo que não for uma definição de função.
        """
        if not code:
            return ""

        try:
            lines_formated = []
            for line in code:
                # strip() remove espaços/tabs antigos nas extremidades para evitar duplicação
                clean_line = line.strip()
                
                # Verifica se a linha é uma definição de função
                if clean_line.startswith("def ") or clean_line.startswith("async def "):
                    lines_formated.append(clean_line)
                else:
                    # Usa 4 espaços (padrão PEP 8) em vez de '\t'
                    # Se a linha já tiver indentação original, o .strip() acima limpou. 
                    # Se quiser manter a indentação interna original, remova o .strip().
                    lines_formated.append("  " + line)

            return "\n".join(lines_formated)

        except Exception as e:
            print(f"Erro ao formatar código: {e}")
            return "\n".join(code)
    # -----------------------------
    # AST PARSER (com FIX 2 🔥)
    # -----------------------------

    def __extrair_blocos(self, code: str):
        """Extrai blocos de código, imports e variáveis de uma string de código Python.
        
        Args:
            code (str): Código fonte Python a ser analisado.
            
        Returns:
            tuple: Tupla contendo três listas:
                - imports: Lista de strings com declarações de importação
                - variables: Lista de strings com declarações de variáveis
                - blocks: Lista de dicionários com informações sobre classes e funções
        """
        try:
            tree = ast.parse(code)

            imports = []
            blocks = []
            variables = []
            
            for node in tree.body:
                # Captura variáveis e atribuições
                # ✅ CAPTURA IMPORTS
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.get_source_segment(code, node))
                    
                elif isinstance(node,(ast.Assign, ast.AnnAssign,ast.AugAssign)):
                    variables.append(ast.get_source_segment(code,node))
                
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    full_class = ast.get_source_segment(code, node)
                    class_header = full_class.split(":", 1)[0] + ":"

                    decoratos = [ast.get_source_segment(code,d) for d in node.decorator_list]
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef,ast.AsyncFunctionDef)):
                            method_code = ast.get_source_segment(code, item)
                            if method_code:
                                methods.append(method_code)
                            
                    blocks.append({
                        "type": "class",
                        "class_header": class_header,
                        "decorators":decoratos,
                        "methods": methods
                    })

                elif isinstance(node, (ast.FunctionDef,ast.AsyncFunctionDef)):
                    methods=[]
                    decorators = [ast.get_source_segment(code,d) for d in node.decorator_list]
                    
                    method_code = ast.get_source_segment(code,node)
                    if method_code:
                        methods.append(method_code)
                                
                    blocks.append({
                        "type": "function",
                        "methods": methods,
                        "decorators":decorators 
                    })

            return imports, variables, blocks
        except Exception as e:
            print(e)
            return [],[],[]


    # -----------------------------
    # PROCESSAMENTO INTELIGENTE (FIX 2 AQUI 🔥)
    # -----------------------------
    
    async def processar_codigo(self, code: str, language: str) -> str:
        """Processa código fonte chamando MCP para documentação.
        
        Divide o código em partes e aplica documentação automática.
        Trata erros de sintaxe e retorna código original em falhas.
        
        Args:
            code: Código fonte a ser documentado
            language: Linguagem de programação do código
            
        Returns:
            Código documentado ou original em caso de falha
        """
        try:
            try:
                if language.lower() != "python":
                    #return self.call_mcp(code=code,language=language)
                    chunks = self.__dividir_codigo_generico(code,language=language)
                else:
                    chunks = self.__dividir_codigo(code)
            except SyntaxError as e:
                result = await self.__call_agent(code, language)
                return result

            resultados = []
            
            if len(chunks)== 0:
                print("Falha ao documenta codigo, retornando codigo original")
                return code
            
            for chunk in chunks:
                result =  await self.__call_agent(chunk,language)
                resultados.append(result)
                
            
            if language.lower() == "python":
                result = self.__formatar_codigo(resultados)
                print(result)
                return result
            
            result = "\n\n".join(resultados)       
            print(result)
            return result
        except Exception as e:
            print(e)
            return code    
    
        
    #Arquivos muito grande são divididos em pequenos pedacos para melhorar trade-offs
    	
    def __dividir_codigo(self, code: str, max_chars=4000):
        """Divide o código fonte em partes menores com base no limite de caracteres.

        Extrai imports, variáveis e blocos de código, e os segmenta em partes
        que não excedam o limite máximo de caracteres especificado.

        Args:
            code: Código fonte a ser dividido.
            max_chars: Número máximo de caracteres por parte (padrão: 4000).

        Returns:
            Lista contendo as partes do código segmentadas.
            Retorna lista vazia em caso de exceção.
        """
        try:
            imports,variables, blocks = self.__extrair_blocos(code=code)
            
            chunks =[]
            base_context= "\n".join(imports + variables+[blocks[0].get('class_header','')])
            
            if base_context:
                chunks.append(base_context)
            
            for block in blocks:
                if len(block["methods"])> 0:
                    for func in block["methods"]:
                        chunk = func
                        chunks.append(chunk)
                continue
            
            final_chunks = []

            for chunk in chunks:
                if len(chunk) <= max_chars:
                    final_chunks.append(chunk)
                else:
                    # fallback bruto (só se necessário)
                    partes = [
                        chunk[i:i+max_chars]
                        for i in range(0, len(chunk), max_chars)
                    ]
                    final_chunks.extend(partes)

            return final_chunks 
        except Exception as e:
            print(e)
            return []

        
    def __extrair_imports(self, code: str, language: str):
        """
        Extrai linhas de importação de código fonte com base na linguagem especificada.

        Args:
            code (str): Código fonte a ser analisado.
            language (str): Linguagem de programação (javascript, java, csharp, go).

        Returns:
            list: Lista de strings contendo as linhas de importação encontradas.
        """
        imports = []

        for line in code.splitlines():
            l = line.strip()

            if language == "javascript":
                # Verifica importações ES6 (import ...) e CommonJS (const ... = require())
                if l.startswith("import ") or (l.startswith("const ") and "require(" in l):
                    imports.append(line)

            elif language == "java":
                # Captura declarações de import e package
                if l.startswith("import ") or l.startswith("package "):
                    imports.append(line)

            elif language == "csharp":
                # Identifica diretivas using para namespaces
                if l.startswith("using "):
                    imports.append(line)

            elif language == "go":
                # Go pode ter blocos de import ou declarações únicas
                # Captura diretivas import e declarações de package
                if l.startswith("import") or l.startswith("package "):
                    imports.append(line)

        return imports

    def __extrair_globais(self, code: str):
        """ Extrai declarações de variáveis globais do código fornecido.

        Analisa o código linha a linha para identificar declarações de variáveis
        no escopo global, considerando linguagens como Go, JavaScript e outras
        onde variáveis podem ser declaradas com 'var', 'const', 'let', ou atribuídas
        com '=' fora de blocos.

        Parâmetros:
        code (str): Código-fonte a ser analisado.

        Retorna:
        list: Lista de strings contendo as linhas que representam declarações
                de variáveis globais.
        """
        globais = []
        nivel = 0

        for line in code.splitlines():
            
            stripped = line.strip()

            # atualiza profundidade
            nivel += line.count("{")
            nivel -= line.count("}")

            if nivel == 0:
                # Para GO, captura var declarations em nível global
                if stripped.startswith("var "):
                    globais.append(line)
                # Para JS, captura const/let/var
                elif stripped.startswith(("const ", "let ", "var ")):
                    globais.append(line)
                # Para todos: variáveis com = fora de blocos
                elif "=" in stripped and not stripped.startswith(("if", "for", "while", "switch", "func", "function", "class")):
                    globais.append(line)

        return globais

    def __extrair_classes(self, code: str):
        """
        Extrai blocos de código correspondentes a definições de classes ou structs.
        
        Este método percorre o código caractere por caractere, identificando blocos
        delimitados por '{' e '}' que correspondem a definições de classes (como em C#,
        Java, JavaScript) ou structs (como em Go).
        
        Args:
            code (str): Código-fonte a ser analisado.
        
        Returns:
            list: Lista de strings contendo os blocos de código extraídos.
        """
        classes = []
        stack = []
        start = None
    
        for i, char in enumerate(code):
            if char == "{":
                if not stack:
                # Pega a linha anterior (ou atual) onde está a definição da classe
                    # Procura desde a última quebra de linha até o { atual
                    last_newline = code.rfind('\n', 0, i)
                    if last_newline == -1:
                        last_newline = 0
                    prefix = code[last_newline:i].strip()
    
                    # Verifica se é uma classe (C#, Java, JS) ou struct (GO)
                    if ("class " in prefix or "struct" in prefix) and (
                        "class " in prefix.split()[0] if prefix.split() else False or
                        "struct" in prefix
                    ):
                        start = i
                stack.append("{")
    
            elif char == "}":
                if stack:
                    stack.pop()
                    if not stack and start is not None:
                        class_code = code[start:i+1].strip()
                        if class_code:
                            classes.append(class_code)
                        start = None
    
        return classes


    	
    def __extrair_metodos(self, classe_code: str):
            """Extrai métodos de uma string contendo código de classe.
        
            Percorre o código caractere por caractere para identificar blocos de métodos
            delimitados por chaves `{}`. Caso não encontre métodos com blocos, procura por
            métodos expression-bodied usando a notação `=>`.
        
            Args:
                classe_code (str): Código-fonte da classe como string.
        
            Returns:
                list: Lista de strings contendo os métodos extraídos.
            """
            metodos = []
            stack = []
            start = None
        
            for i, char in enumerate(classe_code):
                if char == "{":
                    if not stack:
                        linha = classe_code[:i].split("\n")[-1]
                        if "(" in linha and ")" in linha:
                            start = i
                    stack.append("{")
        
                elif char == "}":
                    if stack:
                        stack.pop()
                        if not stack and start is not None:
                            metodos.append(classe_code[start:i+1])
                            start = None
                
            # Se não encontrou métodos com {}, procura por métodos expression-bodied (=>)
            if not metodos:
                linhas = classe_code.split('\n')
                for linha in linhas:
                    linha = linha.strip()
                    # Verifica se é uma linha de método
                    if any(mod in linha for mod in ['public ', 'private ', 'protected ', 'internal ']):
                        if '(' in linha and ')' in linha and '=>' in linha:
                            metodos.append(linha)
                
            return metodos



    def __dividir_codigo_generico(self, code: str, language: str):
        """
        Divide o código fonte em partes menores, priorizando a extração de classes e métodos.

        Este método extrai imports, variáveis globais, classes e métodos do código fornecido,
        e os reorganiza em blocos individuais. Caso não sejam encontrados métodos ou classes,
        o código é dividido em partes menores com base em um limite de caracteres.

        Parâmetros:
            code (str): Código fonte a ser dividido.
            language (str): Linguagem de programação do código.

        Retorna:
            list: Lista de strings, onde cada string representa um bloco ou chunk do código.
        """
        imports = self.__extrair_imports(code, language)
        globais = self.__extrair_globais(code)

        base_context = "\n".join(imports + globais)

        chunks = []

        classes = self.__extrair_classes(code)

        for classe in classes:
            # pega header da classe
            header = classe.split("{", 1)[0] + "{"

            metodos = self.__extrair_metodos(classe)

            for metodo in metodos:
                chunk = base_context + "\n\n" + header + "\n" + metodo + "\n}"
                chunks.append(chunk)

        # Fallback: se não encontrou métodos, retorna o código original em chunks menores
        if not chunks:
            # Divide o código em pedaços de 2000 caracteres
            for i in range(0, len(code), 2000):
                chunks.append(code[i:i+2000])
        
        return chunks


    def extrair_funcoes_soltas(self, code: str, language: str):
            """Extrai funções que não estão dentro de classes
        
            Args:
                code (str): Código-fonte a ser analisado.
                language (str): Linguagem de programação do código-fonte. Ex: 'go', 'javascript'.
        
            Returns:
                list: Lista de strings contendo as funções extraídas.
            """
            funcoes = []
            
            import re
            
            if language == "go":
                # Go: func nome(params) retorno { corpo }
                pattern = r'func\s+\w+\s*\([^)]*\)\s*\{[^}]*\}'
                matches = re.finditer(pattern, code, re.DOTALL)
                for match in matches:
                    funcoes.append(match.group())
            
            elif language == "javascript":
                # JS: function nome(params) { corpo } ou const nome = () => { corpo }
                patterns = [
                    r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*\}',
                    r'const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\}',
                    r'let\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\}'
                ]
                for pattern in patterns:
                    matches = re.finditer(pattern, code, re.DOTALL)
                    for match in matches:
                        funcoes.append(match.group())
            
            return funcoes
