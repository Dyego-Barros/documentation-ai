import requests
import json
import re
import ast

class documentationPython:
    # -----------------------------
    # MCP CALL (sem mudança)
    # -----------------------------
    def call_mcp(self, code: str, language: str) -> str:
        
        MCP_URL = "http://localhost:9000/mcp"

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
        try:
            tree = ast.parse(code)

            imports = []
            blocks = []
            variables = []
        

            for node in tree.body:
                #Captura variaveis
            
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
                        if isinstance(item, ast.FunctionDef):
                            method_code = ast.get_source_segment(code, item)
                            if method_code:
                                methods.append(method_code)
                        
                    blocks.append({
                        "type": "class",
                        "class_header": class_header,
                        "decorators":decoratos,
                        "methods": methods
                    })

                elif isinstance(node, ast.FunctionDef):
                    methods=[]
                    decorators = [ast.get_source_segment(code,d) for d in node.decorator_list]
                    for item in node.body:
                        if isinstance(item,ast.FunctionDef):
                            method_code = ast.get_source_segment(code,item)
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
    def processar_codigo(self, code: str, language: str) -> str:
        try:
            try:
                if language.lower() != "python":
                    #return self.call_mcp(code=code,language=language)
                    chunks = self.dividir_codigo_generico(code,language=language)
                else:
                    chunks = self.dividir_codigo(code)
            except SyntaxError as e:
                print(e)
                return self.call_mcp(code, language)

            resultados = []
            
            if len(chunks)== 0:
                print("Falha ao documenta codigo, retornando codigo original")
                return code
            
            for chunk in chunks:
                result = self.call_mcp(chunk,language)
                resultados.append(result)

            return "\n\n".join(resultados)
        except Exception as e:
            print(e)
            return code
        
    #Arquivos muito grande são divididos em pequenos pedacos para melhorar trade-offs
    def dividir_codigo(self, code: str, max_chars=4000):
        try:
            imports,variables, blocks = self.extrair_blocos(code=code)
            
            if len(imports + variables +blocks) == 0:
                print("Não foi possivel extrair blocos do codigo fornecido!")
                return code
            
            chunks =[]
            base_context= "\n".join(imports + variables)
            
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
        
    def extrair_imports(self, code: str, language: str):
        imports = []

        for line in code.splitlines():
            l = line.strip()

            if language == "javascript":
                if l.startswith("import ") or l.startswith("const ") and "require(" in l:
                    imports.append(line)

            elif language == "java":
                if l.startswith("import ") or l.startswith("package "):
                    imports.append(line)

            elif language == "csharp":
                if l.startswith("using "):
                    imports.append(line)

            elif language == "go":
                # Go pode ter import block ou import único
                if l.startswith("import") or l.startswith("package "):
                    imports.append(line)

        return imports

    def extrair_globais(self, code: str):
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

    def extrair_classes(self, code: str):
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

    def extrair_metodos(self, classe_code: str):
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


    def dividir_codigo_generico(self, code: str, language: str):
        imports = self.extrair_imports(code, language)
        globais = self.extrair_globais(code)

        base_context = "\n".join(imports + globais)

        chunks = []

        classes = self.extrair_classes(code)

        for classe in classes:
            # pega header da classe
            header = classe.split("{", 1)[0] + "{"

            metodos = self.extrair_metodos(classe)

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
        """Extrai funções que não estão dentro de classes"""
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