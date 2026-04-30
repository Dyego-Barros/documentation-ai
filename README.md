# 🚀 VSCode AI Extension – Documentação e Docker Automation

## 📌 Sobre o Projeto

Esta extensão para o Visual Studio Code foi desenvolvida com o objetivo de **automatizar a documentação de código utilizando Inteligência Artificial**, além de **gerar arquivos Docker de forma inteligente** com base na estrutura do projeto.

A extensão é capaz de:

* 📖 Gerar **documentação automática (docstrings / comentários)** para:

  * Python
  * Java
  * JavaScript / TypeScript
  * Go

* 🐳 Gerar automaticamente:

  * `Dockerfile` para projetos individuais
  * `Dockerfile` para múltiplos projetos abertos no mesmo workspace
  * `docker-compose.yml` baseado na estrutura do projeto

---

## 🧠 Arquitetura da Solução

A solução foi projetada com uma arquitetura desacoplada e escalável:

### 🔹 1. Extensão VSCode

Responsável por:

* Interagir com o usuário
* Coletar arquivos e contexto do projeto
* Enviar requisições para a API

---

### 🔹 2. API (FastAPI)

* Atua como ponte entre a extensão e o servidor MCP
* Padroniza requisições
* Simplifica a comunicação

---

### 🔹 3. Servidor MCP (Model Context Protocol)

* Contém as **tools** responsáveis por:

  * Geração de documentação
  * Geração de Dockerfile
  * Geração de docker-compose
* Possui internamente um **Agente de IA (padrão OpenAI)** que:

  * Interpreta o código
  * Executa as tools
  * Gera as respostas inteligentes

📌 **Importante:**
* O agente de IA **não é um serviço separado** — ele faz parte da estrutura interna do MCP, não possuindo um container dedicado.
---

---

### 🔹 4. Modelos (Modelos de LLM usados Context)

* Neste projeto eu testei os seguintes modelos:

  * Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf (Usado para rodar somente usando a CPU)
  * qwen/qwen3-32b (Usando a API do Groq)
  


📌 **Importante:**

* Teste e use com o modelo que preferir **não é obrigado a usar os mesmo modelos**.
---

## Variáveis de ambiente (.env)

Crie um arquivo .env na raiz do projeto, adicione as seguintes variáveis.

```
API_KEY=
USERNAME=
PASSWORD=
BASE_URL=
DEFAULT_URL= 
MODEL_DEFAULT= 
GROQ_MODEL=

```
---
---

## 🐳 Exemplo de `docker-compose.yml`

Abaixo um modelo atualizado para subir os serviços corretamente:

```yaml id="0gqk8z"
version: "3.9"

services:

  api:
    build: ./api
    container_name: ai-api
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app
    environment:
       USERNAME: ${USERNAME}
       PASSWORD: ${PASSWORD}
    depends_on:
      - mcp-server
    restart: always
    networks:
      extension:
        aliases:
          - "api"
    

  mcp-server:
    build: ./mcp
    container_name: mcp-server
    ports:
      - "9000:9000"
    volumes:
      - ./mcp:/app
    environment:
       API_KEY: ${API_KEY}
       BASE_URL: ${BASE_URL}
       DEFAULT_URL: ${DEFAULT_URL}
       MODEL_DEFAULT: ${MODEL_DEFAULT}
       GROQ_MODEL: ${GROQ_MODEL}
    restart: always
    networks:
      extension:
        aliases:
          - "mcp-server"
    

networks:
  extension:

    
```

---

## ⚙️ Como Rodar o Projeto

### 1. Clonar o repositório

```bash id="h5r7zl"
git clone <seu-repo>
cd <seu-repo>
```

### 2. Subir os serviços

```bash id="xax7fk"
docker-compose up --build
```

---

## 🧩 Como instalar a extensão no VSCode

### 🔹 Método 1 – Via arquivo `.vsix`

1. Gere o pacote:

```bash id="19h1yr"
vsce package
```

2. No VSCode:

* Vá em **Extensions**
* Clique nos `...`
* Clique em **Install from VSIX**
* Selecione o arquivo `.vsix`

---

### 🔹 Método 2 – Via terminal

```bash id="9abxhs"
code --install-extension sua-extensao-0.0.1.vsix
```

---

## 🧪 Como usar a extensão

Após instalada:

1. Abra um projeto no VSCode
2. Clique com o botão direito em um arquivo ou pasta
3. Escolha:

   * **Gerar Documentação**
   * **Gerar Dockerfile**
   * **Gerar Docker Compose**

---

## 📌 Benefícios

* ⏱️ Redução de tempo na escrita de documentação
* 📚 Padronização automática
* 🐳 Facilidade na criação de ambientes Docker
* 🧠 Uso de IA para agilizar

---

## 🔮 Futuras melhorias

* Suporte a mais linguagens
* Integração com CI/CD
* Deploy automático
* Customização de templates

---

## 👨‍💻 Autor

Projeto desenvolvido, baseado em algumas necessidades básicas do meu dia a dia, fique a vontade para explorar e plugar os seus agentes de AI, melhorias e sugestões são bem vindas.

---
