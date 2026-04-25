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

def gerar_docstring(code: str) -> str:
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

                Código:
                {code}
"""
            }
        ],
        temperature=0.1,
        top_p=0.8
    )

    return response.choices[0].message.content.strip()