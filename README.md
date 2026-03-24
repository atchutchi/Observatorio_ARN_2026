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
docker-compose up --build
```

### Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **Django Admin**: http://localhost:8000/admin/
- **Nginx (produção)**: http://localhost:80

### Credenciais padrão

- **Admin**: admin / admin123

## Variáveis de Ambiente

Ver `.env.example` para a lista completa.

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

## Development Log

### Fase 1: Fundação — Mar 2026
**Changes:** Setup inicial do projecto com Django backend, Next.js frontend, Docker Compose, modelos de dados (accounts, operators, indicators, data_entry), autenticação JWT, seed data, layout base com sidebar e dashboard esqueleto.
**Decisions:** Monorepo com backend/ e frontend/ separados. JWT para autenticação API. ECharts para gráficos. Docker Compose completo desde o início.
**Status:** Em desenvolvimento.
**Next:** Fase 2 — Entrada de dados (formulários dinâmicos, upload Excel, ETL).
