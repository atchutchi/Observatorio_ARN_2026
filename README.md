# Observatório do Mercado de Telecomunicações da Guiné-Bissau

Plataforma web para o **Observatório do Mercado de Telecomunicações**, gerida pela **ARN (Autoridade Reguladora Nacional)** da Guiné-Bissau.

## Tech Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 5 + Django REST Framework |
| Frontend | Next.js 14 (App Router) + TypeScript |
| Styling | Tailwind CSS + Shadcn/ui |
| Charts | Apache ECharts |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 + Celery |
| Reports | WeasyPrint (PDF) + openpyxl (Excel) |
| AI | Google Gemini (gemini-2.0-flash) |
| Infra | Docker Compose + Nginx |

## Operadores

- **Telecel** (ex-MTN) — Operador Terrestre Completo
- **Orange Bissau** — Operador Terrestre Completo
- **Starlink** (SpaceX) — Operador Satélite / ISP

## Começar

### Pré-requisitos

- Docker e Docker Compose
- Git

### Instalação

```bash
git clone <repo-url>
cd Observatorio_ARN_2026
cp .env.example .env
# Editar .env com as suas credenciais (ver secção abaixo)
docker-compose up --build
```

### Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **Django Admin**: http://localhost:8000/admin/
- **Nginx (produção)**: http://localhost:80

### Primeiro Login

As credenciais do superuser são definidas nas variáveis de ambiente `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` e `DJANGO_SUPERUSER_PASSWORD` no ficheiro `.env`. Altere-as antes do primeiro deploy.

## Variáveis de Ambiente

Ver `.env.example` para a lista completa. Variáveis obrigatórias:

| Variável | Descrição |
|----------|-----------|
| `DJANGO_SECRET_KEY` | Chave secreta Django (gerar com `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `POSTGRES_PASSWORD` | Password da base de dados |
| `DJANGO_SUPERUSER_PASSWORD` | Password do admin (definida no primeiro arranque) |
| `GEMINI_API_KEY` | Chave Google AI Studio (gratuita em aistudio.google.com) — necessária para o chatbot IA |

## Desenvolvimento

### Backend (Django)

```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_data
```

### Frontend (Next.js)

```bash
docker-compose exec frontend npm run dev
```

## API Endpoints

Todos os endpoints estão sob `/api/v1/`:

| Recurso | Endpoints |
|---------|-----------|
| Auth | `POST auth/token/`, `POST auth/token/refresh/`, `GET auth/profile/` |
| Operadores | `GET operators/`, `GET operator-types/` |
| Indicadores | `GET indicator-categories/`, `GET indicators/` |
| Dados | `GET/POST data/`, `GET/POST cumulative-data/`, `POST uploads/` |
| Dashboard | `GET dashboard/summary/`, `GET dashboard/indicator/{cat}/`, `GET dashboard/market-share/`, `GET dashboard/trends/`, `GET dashboard/comparative/`, `GET dashboard/hhi/`, `GET dashboard/export/` |
| Relatórios | `GET reports/`, `POST reports/generate/`, `GET reports/{id}/download_pdf/` |
| Assistente IA | `POST assistant/query/`, `GET assistant/sessions/` |

## Development Log

### Fase 1: Fundação — Mar 2026
**Changes:** Setup inicial com Django backend, Next.js frontend, Docker Compose, modelos de dados (accounts, operators, indicators, data_entry), autenticação JWT, seed data, layout base com sidebar e dashboard esqueleto.
**Decisions:** Monorepo com backend/ e frontend/ separados. JWT para autenticação API. ECharts para gráficos. Docker Compose completo desde o início.
**Status:** Completo.

### Fase 2: Entrada de Dados — Mar 2026
**Changes:** Formulários dinâmicos filtrados por perfil de operador, upload e ETL de ficheiros Excel, mapeamento MTN → Telecel, validação de dados, histórico de uploads.
**Decisions:** Pipeline ETL com Pandas + openpyxl. Validação configurável por indicador.
**Status:** Completo.

### Fase 3: Dashboard e Análise — Mar 2026
**Changes:** DashboardService com agregação ORM (summary, indicator_data, market_share, trends, growth_rates, HHI). 7 endpoints API. Wrappers ECharts (bar, line, pie, combo). Dashboard principal com KPIs reais. Análise por categoria e comparativa. Sidebar com sub-menu análise.
**Decisions:** Serviço centralizado sem modelos próprios. ECharts wrappers reutilizáveis.
**Status:** Completo.

### Fase 4: Relatórios e Exportação — Mar 2026
**Changes:** Modelos Report + ReportTemplate. Geradores PDF (WeasyPrint) e Excel (openpyxl). Celery task para geração assíncrona. Templates HTML. Frontend com lista e formulário de geração com polling.
**Decisions:** WeasyPrint para PDF (HTML → PDF). Geração assíncrona via Celery.
**Status:** Completo.

### Fase 5: Chatbot IA — Mar 2026
**Changes:** Modelos ChatSession + ChatMessage. GeminiAssistant com context builder (dados do DashboardService). Fallback sem API configurada. Interface de chat completa no frontend.
**Decisions:** Google Gemini (modelo gratuito gemini-2.0-flash). Fallback contextual sem API key.
**Status:** Completo.

### Fase 6: Correcções de Segurança e Polish — Mar 2026
**Changes:** Corrigido alerta GitGuardian (credenciais hardcoded removidas do entrypoint.sh). Novas chaves e passwords geradas. Dependências em falta adicionadas (weasyprint, matplotlib, seaborn, google-generativeai). Corrigido bug de market-share no endpoint comparativo. Corrigido memory leak de polling na geração de relatórios. Imports não usados removidos. Tratamento de erros melhorado com toast notifications.
**Status:** Completo.
**Next:** Testes de integração, importação de dados históricos, deploy.

---

*Desenvolvido por: Atchutchi / DCSI ARN*
