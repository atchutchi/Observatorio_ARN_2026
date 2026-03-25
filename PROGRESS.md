# Progresso do Projecto — Observatório Telecom GB

> Documento de referência para acompanhar o estado de cada fase, bugs conhecidos e próximos passos.
> Actualizado a cada sessão de desenvolvimento.

---

## Visão Geral das Fases

| Fase | Descrição | Estado | Data |
|------|-----------|--------|------|
| 1 | Fundação (Django, Docker, Modelos, Auth, Seed) | ✅ COMPLETO | Mar 2026 |
| 2 | Entrada de Dados (Formulários, Upload Excel, ETL) | ✅ COMPLETO | Mar 2026 |
| 3 | Dashboard e Análise | ✅ COMPLETO | Mar 2026 |
| 4 | Relatórios e Exportação (PDF + Excel + Word) | ✅ COMPLETO | Mar 2026 |
| 5 | Chatbot IA (Gemini) | ✅ COMPLETO | Mar 2026 |
| 6 | Correcções de Segurança e Polish | ✅ COMPLETO | 24 Mar 2026 |
| 7 | Funcionalidades Avançadas + Testes | ✅ COMPLETO | 25 Mar 2026 |
| 8 | Desenvolvimento local + estabilização de login | ✅ COMPLETO | 25 Mar 2026 |

---

## Fase 1 — Fundação ✅

### O que foi feito
- Setup Django 5 + Django REST Framework
- Setup Next.js 14 (App Router) + TypeScript + TailwindCSS
- Docker Compose completo (backend, frontend, db, redis, celery, nginx)
- Modelos: `accounts` (User com roles), `operators` (Operator, OperatorType), `indicators` (IndicatorCategory, Indicator, OperatorTypeIndicator, Period)
- Autenticação JWT (SimpleJWT) com refresh token
- Seed data (`seed_data` management command) — 3 operadores + categorias + indicadores
- Layout base: sidebar, header, dashboard esqueleto
- API v1 com DRF routers

### Ficheiros chave
- `backend/config/settings/base.py` — configurações
- `backend/apps/accounts/models.py` — modelo User
- `backend/apps/operators/models.py` — Operator, OperatorType
- `backend/apps/indicators/models.py` — IndicatorCategory, Indicator, OperatorTypeIndicator, Period
- `backend/apps/operators/management/commands/seed_data.py` — seed

---

## Fase 2 — Entrada de Dados ✅

### O que foi feito
- Modelos: `DataEntry`, `CumulativeData`, `FileUpload`, `DataValidationRule`
- ETL pipeline para ficheiros Excel (Telecel/Orange/Starlink)
- Mapeamento MTN → Telecel nos imports
- Formulários dinâmicos filtrados por perfil de operador
- Validação de dados (regras configuráveis)
- Páginas frontend: manual entry, upload, validation, history

### Ficheiros chave
- `backend/apps/data_entry/models.py`
- `backend/apps/data_entry/etl/` — processadores Excel
- `frontend/src/app/(dashboard)/data-entry/` — 4 páginas

---

## Fase 3 — Dashboard e Análise ✅

### O que foi feito
- **Backend `dashboards` app**: `DashboardService` com métodos reais de agregação ORM
  - `get_summary` — KPIs resumo
  - `get_indicator_data` — dados por categoria
  - `get_market_share` — quota de mercado (mobile, fixed_internet, revenue)
  - `get_trends` — evolução temporal
  - `get_growth_rates` — taxas de crescimento
  - `get_hhi` — índice de concentração
  - `get_cagr` — **NOVO** Taxa de Crescimento Anual Composta (CAGR)
- **8 endpoints API**: summary, indicator/{category}, market-share, trends, comparative, cagr, hhi, export
- **Frontend charts**: Wrappers ECharts reutilizáveis (BarChart, LineChart, PieChart, ComboChart, ChartWrapper)
- **Dashboard principal**: KPIs, gráficos de tendência e quota — dados reais da API
- **Análise por indicador**: `/analysis/[category]` com tabela, gráficos evolução/comparação/quota
- **Análise comparativa**: `/analysis/comparative` com HHI e crescimento
- **Análise de mercado**: `/analysis/market` — **NOVO** HHI, quotas, evolução, CAGR por mercado
- **Sidebar**: Sub-menu de análise com 11 categorias + Comparativa + Mercado

---

## Fase 4 — Relatórios e Exportação ✅

### O que foi feito
- **Modelos**: `Report` (com estado, ficheiros PDF/Excel/Word, secções JSON) + `ReportTemplate`
- **PDF generator** (`PDFReportGenerator`): WeasyPrint + templates HTML + gráficos matplotlib
- **Excel generator** (`ExcelReportGenerator`): openpyxl com formatação profissional
- **Word generator** (`DocxReportGenerator`): **NOVO** python-docx com capa, resumo, tabelas, HHI
- **Chart generator** (`chart_generator.py`): **NOVO** matplotlib/seaborn gráficos estáticos (quotas, tendências, HHI)
- **Celery task**: Geração assíncrona de PDF + Excel + Word com actualização de estado
- **Templates HTML**: `quarterly_report.html`, `annual_report.html`
- **Frontend**: Lista de relatórios com download PDF/Excel/Word + formulário de geração com polling

### Ficheiros chave
- `backend/apps/reports/services/pdf_generator.py`
- `backend/apps/reports/services/excel_generator.py`
- `backend/apps/reports/services/docx_generator.py` — **NOVO**
- `backend/apps/reports/services/chart_generator.py` — **NOVO**
- `frontend/src/app/(dashboard)/reports/page.tsx` — botão Word adicionado

---

## Fase 5 — Chatbot IA ✅

### O que foi feito
- **Modelos**: `ChatSession` + `ChatMessage` com FK, metadata JSON
- **Serviço Gemini**: `GeminiAssistant` com `build_context()` (usa DashboardService), `query()` com histórico, fallback sem API
- **Endpoints**: POST `/assistant/query/`, GET `/assistant/sessions/` (ReadOnly)
- **Frontend**: Chat completo com nova conversa, suggested queries, mensagens

---

## Fase 6 — Correcções, Segurança e Polish ✅

### Correcções de Segurança — 24 Mar 2026
- [x] **GitGuardian Alert**: Removidas credenciais hardcoded (`admin`/`admin123`) do `backend/entrypoint.sh`
- [x] Entrypoint agora exige variáveis de ambiente obrigatórias (sem defaults inseguros)
- [x] Novas passwords seguras geradas no `.env`
- [x] Nova `DJANGO_SECRET_KEY` gerada
- [x] Chave Gemini removida do `.env` (deve ser adicionada pelo utilizador)
- [x] `.env` confirmado fora do tracking git

### Correcções de Bugs — 24 Mar 2026
- [x] README actualizado (removidas credenciais padrão, documentadas fases 2-5)
- [x] Adicionadas dependências em falta: `weasyprint`, `matplotlib`, `seaborn`, `google-generativeai`
- [x] Corrigido bug comparative market-share mapping (category_code → market key via mapping dict)
- [x] Corrigido polling leak no `reports/generate/page.tsx` (useRef + cleanup no useEffect)
- [x] Removidos imports não usados (`BarChart` em [category], `json` em ai_assistant)
- [x] Removida API call redundante (`shareRes` em comparative)
- [x] Adicionado tratamento de erros com `toast` em páginas de análise

---

## Fase 7 — Funcionalidades Avançadas + Testes ✅ — 25 Mar 2026

### Prioridade Alta — Implementado

#### Página de Perfil (`/profile`)
- [x] Página completa de perfil com edição inline (nome, email, telefone, cargo)
- [x] Chamada PATCH `/auth/profile/` para actualização
- [x] Link no avatar do header para a página de perfil
- [x] Visualização de role, operador, informações da conta

#### Gestão de Utilizadores (`/settings/users`)
- [x] Página CRUD completa: lista, criar, editar, eliminar utilizadores
- [x] Modal de criação/edição com todos os campos (role, operador, password)
- [x] Pesquisa por nome/username/email
- [x] Filtro por perfil de acesso (role)
- [x] Protecção: só admin ARN tem acesso
- [x] Validação: não pode eliminar a própria conta

#### Página de Configurações (`/settings`)
- [x] Visão geral com KPIs (utilizadores, operadores, categorias)
- [x] Tab de operadores — lista com cores, códigos, estado
- [x] Tab de categorias — lista com tipo (mensal/cumulativo), código, contagem
- [x] Links rápidos para gestão de utilizadores e geração de relatórios
- [x] Sidebar com sub-menu (Visão Geral + Utilizadores)

#### Relatórios Word (.docx)
- [x] `DocxReportGenerator` com python-docx: capa, resumo executivo, tabelas, HHI
- [x] Endpoint `download_docx` no `ReportViewSet`
- [x] Campo `docx_file` no modelo `Report` + migração
- [x] Geração automática na task Celery (PDF + Excel + Word)
- [x] Serializer actualizado com `docx_url`
- [x] Botão "Word" na lista de relatórios (frontend)
- [x] Dependência `python-docx==1.1.2` adicionada ao `requirements.txt`

#### Testes Unitários e de Integração
- [x] **accounts/tests/test_models.py** — roles, propriedades, campos User
- [x] **accounts/tests/test_views.py** — auth (tokens, refresh), profile (get/patch), gestão users (CRUD, permissões)
- [x] **dashboards/tests/test_services.py** — summary, market share, HHI, growth rates, CAGR
- [x] **dashboards/tests/test_views.py** — todos os endpoints dashboard (summary, market-share, hhi, cagr, trends, export)
- [x] **indicators/tests/test_models.py** — categorias, indicadores, períodos, hierarquia, unique constraints
- [x] **data_entry/tests/test_models.py** — DataEntry, CumulativeData, unique constraints, history tracking
- [x] **reports/tests/test_views.py** — lista, retrieve, generate, publish, download, permissões

### Prioridade Média — Implementado

#### CAGR (Crescimento Anual Composto)
- [x] `DashboardService.get_cagr()` — fórmula `((V_end/V_start)^(1/n) - 1) × 100`
- [x] Endpoint GET `/dashboard/cagr/` com parâmetros `category`, `start_year`, `end_year`
- [x] CAGR por operador + total de mercado

#### Análise de Mercado (`/analysis/market`)
- [x] Página completa com HHI, quota, evolução, crescimento
- [x] Selecção de 7 mercados (móvel, voz, SMS, dados, internet fixo, receitas, emprego)
- [x] KPIs: HHI, classificação, líder de mercado
- [x] Gráficos: quota (pie), evolução HHI (line), evolução operadores (combo), crescimento (bar)
- [x] Tabela de detalhe com barras de quota visual

#### Gráficos Estáticos para PDFs (Matplotlib/Seaborn)
- [x] `chart_generator.py` — gera gráficos PNG em base64
- [x] Quotas de mercado (pie chart) para mobile, internet fixo, receitas
- [x] Tendências (stacked bar + line) para estações móveis, tráfego, receitas
- [x] Indicador HHI (horizontal bar com thresholds)
- [x] Integrados no `PDFReportGenerator._build_context()`

### Prioridade Baixa — Implementado

#### Rate Limiting API
- [x] DRF throttling configurado: `anon: 30/min`, `user: 120/min`
- [x] `AnonRateThrottle` + `UserRateThrottle` em `DEFAULT_THROTTLE_CLASSES`

#### Auditoria (django-simple-history)
- [x] `django-simple-history==3.7.0` adicionado ao `requirements.txt`
- [x] `simple_history` em `INSTALLED_APPS`
- [x] `HistoryRequestMiddleware` no middleware stack
- [x] `HistoricalRecords` em `DataEntry` e `CumulativeData`
- [x] Tracking automático de todas as alterações de dados

#### Dependências Adicionadas
```
python-docx==1.1.2       # Word report generation
reportlab==4.2.5          # Alternative PDF generation
django-simple-history==3.7.0  # Audit trail
```

---

## Fase 8 — Desenvolvimento local + estabilização de login ✅ — 25 Mar 2026

### Dados reais e identidade visual (continuação)
- [x] Logos ARN, Orange e Telecel em `frontend/public/logos/` e `backend/static/logos/`
- [x] Ficheiros JSON KPI 2024 (`backend/data/kpi_2024/`) — Orange e Telecel
- [x] Comando `import_kpi_json` — importação para `DataEntry` / `CumulativeData` + totais raiz para o dashboard
- [x] `entrypoint.sh` — `seed_data` e `import_kpi_json` no arranque Docker (quando aplicável)

### Arranque local sem Docker
- [x] Script `start.sh` na raiz: `./start.sh setup` (venv, pip, migrate, seed, KPI, superuser, npm), `./start.sh` (backend + frontend), `./start.sh backend|frontend|stop`
- [x] Backend: `USE_SQLITE=true` + `DJANGO_SETTINGS_MODULE=config.settings.development` para SQLite em `backend/db.sqlite3`
- [x] **Importante**: `npm run dev` corre em `frontend/`; `manage.py` corre em `backend/` — na raiz do repo não existe `package.json` nem `manage.py`
- [x] `.gitignore` — pasta `.pids/` (PIDs do script de arranque)

### Correcções de autenticação (login → dashboard)
- [x] **Axios** (`frontend/src/lib/api.ts`): não enviar header `Authorization` nos pedidos a `/auth/token` (tokens antigos no `localStorage` causavam 401 no login)
- [x] **Login** (`login/page.tsx`): `trim()` em utilizador e palavra-passe; mensagem de erro mais clara
- [x] **Perfil 403**: `UserViewSet` usa `IsARNAdmin` a nível de classe; o URL manual `auth/profile/` não aplicava `permission_classes=[IsAuthenticated]` da action — o utilizador criado com `role='ADMIN_ARN'` não correspondia a `'admin_arn'` nas `ROLE_CHOICES`, logo `is_arn_admin` era falso e `/auth/profile/` devolvia 403; `fetchProfile()` limpava os tokens e o utilizador ficava preso no login
- [x] **Superuser**: corrigido `start.sh` para definir `role = 'admin_arn'` ao criar admin; utilizadores existentes devem ter `role` exactamente `admin_arn` (minúsculas, conforme modelo)

### Ficheiros tocados (referência)
- `start.sh`, `.gitignore`, `frontend/src/lib/api.ts`, `frontend/src/app/(auth)/login/page.tsx`

---

## Arquitectura do Projecto

```
Observatorio_ARN_2026/
├── backend/
│   ├── apps/
│   │   ├── accounts/        ✅ User, roles, auth, profile, CRUD users
│   │   │   └── tests/       ✅ test_models.py, test_views.py
│   │   ├── operators/       ✅ Operator, OperatorType, seed_data
│   │   ├── indicators/      ✅ IndicatorCategory, Indicator, Period
│   │   │   └── tests/       ✅ test_models.py
│   │   ├── data_entry/      ✅ DataEntry, CumulativeData, FileUpload, ETL, History
│   │   │   └── tests/       ✅ test_models.py
│   │   ├── dashboards/      ✅ DashboardService (+CAGR), views (+CAGR), urls
│   │   │   └── tests/       ✅ test_services.py, test_views.py
│   │   ├── reports/         ✅ Report (+docx), PDF/Excel/Word generators, Charts
│   │   │   ├── services/    ✅ pdf_generator, excel_generator, docx_generator, chart_generator
│   │   │   └── tests/       ✅ test_views.py
│   │   ├── ai_assistant/    ✅ ChatSession, ChatMessage, GeminiAssistant
│   │   └── api/v1/          ✅ Routers, URLs aggregation
│   ├── config/              ✅ Settings (+throttling, +audit), URLs, Celery, WSGI
│   └── templates/reports/   ✅ quarterly_report.html, annual_report.html
├── frontend/src/
│   ├── app/(auth)/login/    ✅ Login page
│   ├── app/(dashboard)/
│   │   ├── page.tsx         ✅ Dashboard principal
│   │   ├── profile/         ✅ NOVO — Página de perfil
│   │   ├── settings/        ✅ NOVO — Configurações admin
│   │   │   └── users/       ✅ NOVO — Gestão de utilizadores
│   │   ├── analysis/
│   │   │   ├── [category]/  ✅ Análise por indicador
│   │   │   ├── comparative/ ✅ Análise comparativa
│   │   │   └── market/      ✅ NOVO — Análise de mercado
│   │   ├── data-entry/      ✅ Manual, Upload, Validation, History
│   │   ├── reports/         ✅ Lista + Geração (+Word download)
│   │   └── assistant/       ✅ Chat IA
│   ├── components/          ✅ Charts (ECharts), Layout, UI, Chat
│   ├── lib/                 ✅ API client (Axios), utils, auth
│   ├── hooks/               ✅ useApi
│   └── types/               ✅ TypeScript interfaces
├── nginx/                   ✅ Reverse proxy config
├── start.sh                 ✅ Arranque local (backend + frontend + setup)
├── backend/data/kpi_2024/   ✅ JSON KPI reais (Orange, Telecel)
└── docker-compose.yml       ✅ Full stack orchestration
```

---

## Próximos Passos

### Restantes (Prioridade Baixa)
1. Multilíngua (PT/FR) — i18n com next-intl ou django translations
2. Views materializadas PostgreSQL — optimização de performance para dashboards
3. Backup automático diário — pg_dump cron job
4. Notificações por email — prazos, submissões, publicações
5. PWA — Progressive Web App (service worker, manifest)
6. LangChain para RAG — optional, para melhorar assistente IA
7. Prophet para forecasting — previsões estatísticas
8. Gráficos específicos (34+) — configurações detalhadas por indicador
9. Testes E2E com Playwright — fluxos completos

### Concluído
- ~~Corrigir alerta GitGuardian~~ ✅
- ~~Adicionar dependências em falta~~ ✅
- ~~Corrigir bugs fase 3-5~~ ✅
- ~~Página de perfil~~ ✅
- ~~Gestão de utilizadores~~ ✅
- ~~Configurações/Admin~~ ✅
- ~~Relatórios Word~~ ✅
- ~~Testes unitários~~ ✅
- ~~CAGR~~ ✅
- ~~Análise de mercado~~ ✅
- ~~Gráficos estáticos PDF~~ ✅
- ~~Rate limiting~~ ✅
- ~~Auditoria~~ ✅
- ~~Desenvolvimento local (`start.sh`, SQLite)~~ ✅
- ~~Login e redireccionamento pós-perfil (Axios + role `admin_arn`)~~ ✅

---

*Última actualização: 25 Mar 2026 (Fase 8 — dev local + auth)*
