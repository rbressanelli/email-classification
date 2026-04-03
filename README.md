# Smart Email Triage

Aplicação web em **Python + FastAPI + HTML/CSS/JS** para classificar emails em **Produtivo** ou **Improdutivo** e sugerir uma resposta automática.

## Visão da solução

Este projeto foi criado como solução para um desafio técnico cujo objetivo é automatizar a leitura e triagem de emails corporativos, reduzindo esforço manual e aumentando a produtividade da equipe.

A aplicação permite:

- colar o conteúdo de um email diretamente na interface;
- fazer upload de arquivos `.txt` e `.pdf`;
- classificar automaticamente o email como **Produtivo** ou **Improdutivo**;
- sugerir uma resposta automática coerente com a classificação;
- exibir sinais detectados, justificativa e nível de confiança.


## Deploy
Acesso à aplicação hospedada online pelo seguinte link:
<a href="https://email-classification-1id1.onrender.com/app">email-classification</a>

### Fluxo principal

1. O usuário cola o texto do email ou faz upload de `.txt`/`.pdf`.
2. O backend extrai o texto.
3. O texto passa por **pré-processamento NLP**:
   - normalização
   - remoção de stopwords
   - stemming em português
4. Um **classificador híbrido** faz a inferência:
   - TF-IDF + Logistic Regression
   - ajuste por regras/keywords de negócio
5. Um **gerador de resposta** devolve:
   - template local, sem custo
   - ou resposta via OpenAI, caso exista `OPENAI_API_KEY`
6. A interface exibe categoria, confiança, justificativa, sinais detectados e resposta sugerida.

## Diferenciais técnicos

- Funciona **sem API paga**, usando classificador local + respostas template.
- Suporta melhoria opcional com **OpenAI** para respostas mais naturais.
- Estrutura separada em camadas para facilitar testes e manutenção.
- Deploy simples em **Render** ou **Hugging Face Spaces (Docker)**.


## Estrutura

```bash
app/
  api/routes.py
  core/config.py
  core/schemas.py
  services/
    classifier.py
    document_reader.py
    orchestrator.py
    preprocessor.py
    reply_generator.py
  static/
    app.js
    styles.css
  templates/
    index.html
  main.py
data/examples/
requirements.txt
render.yaml
Dockerfile
tests/
README.md
```

## Como rodar localmente

### 1. Clonar o projeto

```bash
git clone <SEU_REPOSITORIO>
cd email-ai-challenge
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Se quiser usar OpenAI para enriquecer a resposta sugerida:

```env
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-4o-mini
```

### 5. Executar

```bash
uvicorn app.main:app --reload
```

Acesse:

- `http://127.0.0.1:8000/app`
- healthcheck em `http://127.0.0.1:8000/health`

## Testes

```bash
pytest
```

## Exemplos para demonstração

- `data/examples/productive_email.txt`
- `data/examples/unproductive_email.txt`

## Melhorias futuras sugeridas

- Persistir histórico de análises em banco.
- Adicionar autenticação e trilha de auditoria.
- Criar classificação multiclasses.
- Treinar o classificador com dataset real rotulado.
- Implementar fila assíncrona para alto volume.
- Integrar com provedores reais de email (Microsoft Graph, Gmail API).

## Melhor opção gratuita para deploy

### Opção recomendada: Render

Motivos:
- aceita **FastAPI** nativamente;
- deploy simples a partir do GitHub;
- suporta aplicações Python dinâmicas;
- possui plano gratuito para projetos pessoais/testes.

### Alternativa excelente: Hugging Face Spaces com Docker

Motivos:
- também possui camada gratuita;
- aceita apps com Docker;
- é especialmente amigável para projetos com AI.

## Roteiro do vídeo de 3 a 5 minutos

### Introdução

- apresentação pessoal;
- resumo do desafio e do objetivo do sistema.

### Demonstração

- abrir a tela inicial;
- colar um email produtivo e mostrar resultado;
- enviar um `.txt` ou `.pdf`;
- mostrar a resposta sugerida;
- repetir com um email improdutivo.

### Explicação técnica

- frontend web simples e intuitivo;
- backend FastAPI;
- pipeline NLP com stemming/stopwords;
- classificador híbrido local;
- uso opcional de OpenAI para melhorar a geração da resposta;
- possibilidade de deploy em Render/HF Spaces.

### Conclusão

- reforçar ganho operacional;
- citar escalabilidade futura;
- comentar aprendizados.

### Executando com Docker

```bash
docker build -t email-ai-challenge .
docker run --rm -p 8000:8000 email-ai-challenge
```

### Executando com Docker Compose

Para maior facilidade no desenvolvimento e gerenciamento do container, você pode usar o **Docker Compose**:

```bash
docker compose up --build
```

Isso irá:
1. Construir a imagem.
2. Carregar as variáveis do arquivo `.env`.
3. Montar os volumes para refletir alterações no código em tempo real (dentro de `app/` e `data/`).
4. Expor a porta `8000`.
