from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    
    #default_headers={"Authorization": f"Basic {credentials}"}
)

def gerar_docstring_Python(code: str) -> str:
    response = client.chat.completions.create(
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você deve é um engenheiro de Software Python Senior. 
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar docstring e comentarios para o código Python fornecido, incluindo classes e metodos e getters e setters, obedeça rigorosamente as regras definidas.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione docstring correta
                - Apenas adicione comentario correto
                - Documente parâmetros e retorno quando existirem
                - Retorne o código completo com os comentários e docstrings adicionados
                - Não explique nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.

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
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você deve é um engenheiro de Software C# Senior. 
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar documentação para o código C# fornecido, obedeça rigorosamente as regras.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione documentação correta
                - Apenas adicione comentario correto
                - Documente parâmetros e retorno quando existirem
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.

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
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
         model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de Software Java Senior.
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar comentários JavaDoc para o código Java fornecido, obedeça rigorosamente as regras.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione comentários JavaDoc corretos (/** */)
                - Documente parâmetros e retorno quando existirem
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.

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
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
         model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de Software JavaScript Senior.
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar comentários JSDoc para o código JavaScript ou TypeScript fornecido, obedeça rigorosamente as regras.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione comentários JSDoc (/** */)
                - Documente parâmetros (@param) e retorno (@returns)
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.
                
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
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
         model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de Software Go (Golang) Senior.
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar comentários idiomáticos do Go para o código fornecido, obedeça rigorosamente as regras.

                REGRAS:
                - Não reescreva funções
                - Não duplique código
                - Não reescreva lógica
                - Apenas adicione comentários acima das funções
                - Use o padrão oficial do Go (comentário começa com o nome da função)
                - Retorne o código completo com os comentários adicionados
                - Não explique nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.

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
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
         model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de DevOps Senior.
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar dockerfile usando multistage, para melhor segurança e desempenho e criação correta das imagens docker.

                REGRAS:
                - Observe a linguagem
                - Observe frameworks utilizados 
                - Use '#' para comentarios 
                - Retorne o dockerfile completo com comentarios
                - Não explique nada
                - Não invente nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.

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
        #model="Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
         model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": f"""
                Você é um engenheiro de DevOps Senior.
                Sua lingua é português do Brasil.
                Sua responsabilidade é gerar docker-compose observando o contexto recebido e estruturar da melhor maneira possivel.

                REGRAS:
                - Observe path de cada service recebido
                - Siga boas patricas 
                - Use '#' para comentarios
                - Sempre adicione comentarios no inicio do arquivo
                - Retorne o docker-compose completo 
                - Não invente nada
                - Não explique nada
                - Não use markdown
                - Não inclua raciocínio interno.
                - Não use <think>.
                - Responda apenas com a resposta final.
                - Return only the final answer. Do not include reasoning, thoughts, or <think> tags.

                dados:
                {services}
                """
            }
        ],
        temperature=0.1,
        top_p=0.8
    )
    
    return response.choices[0].message.content.strip()