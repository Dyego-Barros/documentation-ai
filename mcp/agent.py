from openai import OpenAI
import base64

username = "dyego"
password = "@Dyego050291#"

credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

client = OpenAI(
    api_key="dummy",
    base_url="https://ia.dmgsoftware.com.br/v1",
    default_headers={"Authorization": f"Basic {credentials}"}
)

def gerar_docstring_Python(code: str) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você deve é um engenheiro de Software Python Senior. 
                Sua responsabilidade é gerar docstring para o código, seja ele uma classe com metodos ou somente metodos independentes.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione docstring correta
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown

                Código:
                {code}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )

    return response.choices[0].message.content.strip()

def gerar_docstring_csharp(code: str) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você deve é um engenheiro de Software C# Senior. 
                Sua responsabilidade é gerar documentação para o código, seja ele uma classe com metodos, ou somente metodos, ou interfaces e demais codigos.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione documentação correta
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown

                Código:
                {code}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )

    return response.choices[0].message.content.strip()
def gerar_docstring_java(code: str) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de Software Java Senior.
                Sua responsabilidade é gerar comentários JavaDoc para o código, seja ele classes, métodos ou interfaces.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione comentários JavaDoc corretos (/** */)
                - Documente parâmetros e retorno quando existirem
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown

                Código:
                {code}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )

    return response.choices[0].message.content.strip()
def gerar_docstring_javascript(code: str) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de Software JavaScript Senior.
                Sua responsabilidade é gerar comentários JSDoc para o código.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione comentários JSDoc (/** */)
                - Documente parâmetros (@param) e retorno (@returns)
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown
                Código:
                {code}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )

    return response.choices[0].message.content.strip()
def gerar_docstring_go(code: str) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de Software Go (Golang) Senior.
                Sua responsabilidade é gerar comentários idiomáticos do Go para o código.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione comentários acima das funções
                - Use o padrão oficial do Go (comentário começa com o nome da função)
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown

                Código:
                {code}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )

    return response.choices[0].message.content.strip()


def gerar_dockerfile(context: dict) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de DevOps Senior.
                Sua responsabilidade é gerar dockerfile usando multistage, para melhor segurança e desempenho e criação correta das imagens docker.

                REGRAS:
                - Observe a linguagem
                - Observe frameworks utilizados 
                - Use padrões ja conhecidos 
                - Não invente nada
                - Sempre adicione uma breve descrição de como funciona o passo escolhido
                - Descrição deve ser sempre no inicio do arquivo
                - Retorne o dockerfile completo com a descrição no inicio do arquivo
                - Não explique nada
                - Não use markdown

                dados:
                {context}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )
    
    return response.choices[0].message.content.strip()


def gerar_compose(services: list) -> str:
    response = client.chat.completions.create(
        model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de DevOps Senior.
                Sua responsabilidade é gerar docker-compose observando o contexto recebido e estruturar da melhor maneira possivel.

                REGRAS:
                - Observe path de cada service recebido
                - Siga boas patricas 
                - Use padrões ja conhecidos 
                - Não invente nada
                - Sempre adicione uma breve descrição de como funciona o passo escolhido, a descrição deve ser no inicio do arquivo
                - Retorne o docker-compose completo 
                - Não explique nada
                - Não use markdown

                dados:
                {services}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )
    
    return response.choices[0].message.content.strip()