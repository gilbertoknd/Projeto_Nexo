# 📜 Histórico e Guia de Comandos — Do Zero ao MVP Operacional
> **Projeto Nexo — Contratação de Serviços com Processamento Assíncrono**  
> Guia cronológico de comandos utilizados desde a concepção do projeto até o estado atual.

---

## 📑 Índice
1. [Fase 1: Ambiente Virtual Python Local (Host)](#fase-1-ambiente-virtual-python-local-host)
2. [Fase 2: Estrutura Inicial do Django (Backend)](#fase-2-estrutura-inicial-do-django-backend)
3. [Fase 3: Infraestrutura e Containers (Docker Compose)](#fase-3-infraestrutura-e-containers-docker-compose)
4. [Fase 4: Testes Automatizados (Pytest no PostgreSQL)](#fase-4-testes-automatizados-pytest-no-postgresql)
5. [Fase 5: Setup do Frontend (Next.js + AntD + React Query)](#fase-5-setup-do-frontend-nextjs--antd--react-query)
6. [Fase 6: Cheat Sheet de Operação e Manutenção do Projeto](#fase-6-cheat-sheet-de-operação-e-manutenção-do-projeto)

---

## Fase 1: Ambiente Virtual Python Local (Host)

Ter um ambiente virtual local (`venv`) no host é a melhor prática para que a IDE (VS Code, PyCharm, etc.) reconheça as bibliotecas instaladas, ofereça *autocompletion*, *type-checking* e *linting*, sem poluir o sistema operacional da sua máquina.

### 1.1. Criar o Ambiente Virtual
Na pasta raiz do projeto ou dentro de `backend/`:

* **No Linux / macOS:**
  ```bash
  cd backend
  python3 -m venv venv
  ```
* **No Windows (PowerShell):**
  ```powershell
  cd backend
  python -m venv venv
  ```

### 1.2. Ativar o Ambiente Virtual
* **No Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```
* **No Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  # Caso o PowerShell bloqueie scripts:
  # Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
* **No Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

### 1.3. Instalação das Dependências e `requirements.txt`
No início do projeto, as dependências são adicionadas conforme as necessidades de arquitetura:

```bash
# 1. Framework Web e APIs
pip install "Django>=5.0,<5.1" djangorestframework django-cors-headers

# 2. Driver do PostgreSQL e Mensageria Assíncrona
pip install psycopg2-binary celery

# 3. Ferramentas de Teste Automatizado
pip install pytest pytest-django

# 4. Congelar versões instaladas no requirements.txt
pip freeze > requirements.txt
```

> **Nota Técnica:** O arquivo `backend/requirements.txt` deste projeto define as dependências de topo declarativas para evitar conflitos de compilação entre SOs (Windows no host vs Linux Debian no Docker):
> ```text
> Django>=5.0,<5.1
> djangorestframework>=3.15
> django-cors-headers>=4.3
> celery>=5.4
> psycopg2-binary>=2.9
> pytest>=8.0
> pytest-django>=4.8
> ```

---

## Fase 2: Estrutura Inicial do Django (Backend)

Com o `venv` ativo, a estrutura inicial do projeto Django e da aplicação de negócios foi gerada:

```bash
cd backend

# Criar o projeto Django 'config' no diretório atual
django-admin startproject config .

# Criar o app 'servicos'
python manage.py startapp servicos

# Criar migrações iniciais dos models (Solicitacao, Proposta, Pagamento)
python manage.py makemigrations servicos

# Validar configurações e integridade do Django
python manage.py check
```

---

## Fase 3: Infraestrutura e Containers (Docker Compose)

O Docker garante que o PostgreSQL 15, o RabbitMQ 3.12, o Django e os Workers Celery rodem isolados e com paridade de produção.

### 3.1. Build das Imagens
```bash
# Na raiz do projeto (onde está o docker-compose.yml):
docker compose build
```

### 3.2. Subir Toda a Stack em Background
```bash
docker compose up -d
```
> **Serviços inicializados:**
> - `db`: PostgreSQL 15 (porta `5432:5432`)
> - `rabbitmq`: RabbitMQ 3.12 (portas `5672:5672` AMQP e `15672:15672` Web Management)
> - `app`: Django REST Framework (porta `8000:8000`)
> - `worker`: Celery Worker conectado ao RabbitMQ
> - `beat`: Celery Beat (Scheduler para crontab 00:00 e 01:00)

### 3.3. Aplicar Migrações no Banco PostgreSQL
```bash
docker compose run --rm app python manage.py migrate
```

---

## Fase 4: Testes Automatizados (Pytest no PostgreSQL)

Seguindo estritamente o **TDD**, os testes unitários do Celery foram criados em `backend/servicos/tests/test_tasks.py` para cobrir os 4 cenários essenciais do MVP.

### 4.1. Execução via Docker (Recomendado)
Executa a suíte de testes dentro do container com o banco PostgreSQL ativo:
```bash
docker compose run --rm app pytest -v
```

### 4.2. Execução Local via `venv` (Host)
Se os containers `db` e `rabbitmq` estiverem rodando no Docker e você quiser rodar os testes localmente pelo terminal da sua IDE:
```bash
cd backend
# Ative o venv e passe o host local para o PostgreSQL:
$env:POSTGRES_HOST="localhost"; pytest -v   # Windows PowerShell
# ou no Linux/Mac:
POSTGRES_HOST=localhost pytest -v
```

---

## Fase 5: Setup do Frontend (Next.js + AntD + React Query)

O frontend foi desenvolvido com Next.js 16 (App Router + Turbopack), TypeScript, Ant Design v6 e React Query v5.

### 5.1. Inicialização do Projeto
Na raiz do projeto:
```bash
npx create-next-app@latest frontend --typescript --app --src-dir --no-tailwind --eslint
```

### 5.2. Instalação das Dependências do Frontend
```bash
cd frontend
npm install antd @ant-design/nextjs-registry @tanstack/react-query
```

### 5.3. Build de Produção
Valida se não há erros de tipagem TypeScript ou de compilação:
```bash
npm run build
```

### 5.4. Executar em Modo de Desenvolvimento
```bash
npm run dev
```
> O app web ficará acessível em: **`http://localhost:3000`**

---

## Fase 6: Cheat Sheet de Operação e Manutenção do Projeto

Comandos rápidos para o dia a dia e para demonstração em entrevistas:

### 🐳 Docker & Backend
| Ação | Comando |
| :--- | :--- |
| **Subir tudo** | `docker compose up -d` |
| **Parar tudo** | `docker compose down` |
| **Ver logs em tempo real do Worker Celery** | `docker compose logs -f worker` |
| **Ver logs do Django (API)** | `docker compose logs -f app` |
| **Acessar o shell interativo do Django** | `docker compose run --rm app python manage.py shell` |
| **Criar novas migrações após alterar models** | `docker compose run --rm app python manage.py makemigrations` |
| **Rodar todos os testes Pytest** | `docker compose run --rm app pytest -v` |

### 🌐 Frontend
| Ação | Comando |
| :--- | :--- |
| **Entrar na pasta e rodar dev server** | `cd frontend && npm run dev` |
| **Validar tipagem e build** | `cd frontend && npm run build` |
| **Instalar nova dependência** | `cd frontend && npm install <pacote>` |

### 🔗 URLs Locais para Teste
* **Frontend Next.js**: [http://localhost:3000](http://localhost:3000)
* **API DRF (Listagem de Solicitações)**: [http://localhost:8000/api/solicitacoes/](http://localhost:8000/api/solicitacoes/)
* **Painel RabbitMQ**: [http://localhost:15672](http://localhost:15672) (usuário: `guest` / senha: `guest`)
