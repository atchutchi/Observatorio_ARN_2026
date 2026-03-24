# Progresso do Projecto — Observatório Telecom GB

> Documento de referência para acompanhar o estado de cada fase, bugs conhecidos e próximos passos.
> Actualizado a cada sessão de desenvolvimento.

---

## Visão Geral das Fases

| Fase | Descrição | Estado | Data |
|------|-----------|--------|------|
| 1 | Fundação (Django, Docker, Modelos, Auth, Seed) | ✅ COMPLETO | Mar 2026 |
| 2 | Entrada de Dados (Formulários, Upload Excel, ETL) | ✅ COMPLETO | Mar 2026 |
| 3 | Dashboard e Análise | ✅ COMPLETO (com bugs a corrigir) | Mar 2026 |
| 4 | Relatórios e Exportação | ✅ COMPLETO (deps em falta) | Mar 2026 |
| 5 | Chatbot IA (Gemini) | ✅ COMPLETO (dep em falta) | Mar 2026 |
| 6 | Correcções de Segurança e Polish | ✅ COMPLETO | 24 Mar 2026 |

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

## Fase 3 — Dashboard e Análise ✅ (com bugs)

### O que foi feito
- **Backend `dashboards` app**: `DashboardService` com métodos reais de agregação ORM
  - `get_summary` — KPIs resumo
  - `get_indicator_data` — dados por categoria
  - `get_market_share` — quota de mercado (mobile, fixed_internet, revenue)
  - `get_trends` — evolução temporal
  - `get_growth_rates` — taxas de crescimento
  - `get_hhi` — índice de concentração
- **7 endpoints API**: summary, indicator/{category}, market-share, trends, comparative, hhi, export
- **Frontend charts**: Wrappers ECharts reutilizáveis (BarChart, LineChart, PieChart, ComboChart, ChartWrapper)
- **Dashboard principal**: KPIs, gráficos de tendência e quota — dados reais da API
- **Análise por indicador**: `/analysis/[category]` com tabela, gráficos evolução/comparação/quota
- **Análise comparativa**: `/analysis/comparative` com HHI e crescimento
- **Sidebar**: Sub-menu de análise com 11 categorias

### 🐛 Bugs Conhecidos — Fase 3
1. **Comparative market-share mapping**: `DashboardComparativeView` passa `cat_code` como `market` para `get_market_share`, mas o serviço espera chaves como `mobile`, `fixed_internet`, `revenue`. Resultado: quota de mercado errada na vista comparativa.
2. **Import não usado**: `[category]/page.tsx` importa `BarChart` mas só usa `ComboChart`, `PieChart` e `LineChart`.
3. **API call não usada**: `comparative/page.tsx` faz `api.get('/dashboard/market-share/')` mas não usa o resultado (`shareRes`).
4. **Tratamento de erros silencioso**: Vários `catch` vazios sem feedback ao utilizador.

---

## Fase 4 — Relatórios e Exportação ✅ (deps em falta)

### O que foi feito
- **Modelos**: `Report` (com estado, ficheiros PDF/Excel, secções JSON) + `ReportTemplate`
- **PDF generator** (`PDFReportGenerator`): Usa WeasyPrint + templates HTML
- **Excel generator** (`ExcelReportGenerator`): Usa openpyxl com formatação profissional
- **Celery task**: Geração assíncrona com actualização de estado
- **Templates HTML**: `quarterly_report.html`, `annual_report.html`
- **Frontend**: Lista de relatórios com download + formulário de geração com polling

### 🐛 Bugs Conhecidos — Fase 4
1. **Dependência WeasyPrint em falta**: `weasyprint` não está no `requirements.txt` — PDF fallback devolve HTML raw.
2. **Dependências matplotlib/seaborn em falta**: Referenciadas no plano mas não implementadas nos geradores (gráficos estáticos).
3. **Polling leak**: Em `reports/generate/page.tsx`, o `setInterval` de polling não é limpo correctamente no `useEffect` — pode continuar após navegação.

---

## Fase 5 — Chatbot IA ✅ (dep em falta)

### O que foi feito
- **Modelos**: `ChatSession` + `ChatMessage` com FK, metadata JSON
- **Serviço Gemini**: `GeminiAssistant` com `build_context()` (usa DashboardService), `query()` com histórico, fallback sem API
- **Endpoints**: POST `/assistant/query/`, GET `/assistant/sessions/` (ReadOnly)
- **Frontend**: Chat completo com nova conversa, suggested queries, mensagens

### 🐛 Bugs Conhecidos — Fase 5
1. **Dependência google-generativeai em falta**: Não está no `requirements.txt` — fallback activo.
2. **ChatSessionViewSet ReadOnly**: Sem CRUD de sessões via API (só criação implícita no POST query).
3. **Import `json` não usado** no `services.py`.

---

## Fase 6 — Correcções, Segurança e Polish 🔄

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

### Dependências em Falta no `requirements.txt`
```
weasyprint          # PDF generation
matplotlib          # Static charts for reports
seaborn             # Statistical charts
google-generativeai # Gemini AI integration
```

---

## Arquitectura do Projecto

```
Observatorio_ARN_2026/
├── backend/
│   ├── apps/
│   │   ├── accounts/        ✅ User, roles, auth
│   │   ├── operators/       ✅ Operator, OperatorType, seed_data
│   │   ├── indicators/      ✅ IndicatorCategory, Indicator, Period
│   │   ├── data_entry/      ✅ DataEntry, CumulativeData, FileUpload, ETL
│   │   ├── dashboards/      ✅ DashboardService, views, urls (sem models)
│   │   ├── reports/         ✅ Report, ReportTemplate, PDF/Excel generators
│   │   ├── ai_assistant/    ✅ ChatSession, ChatMessage, GeminiAssistant
│   │   └── api/v1/          ✅ Routers, URLs aggregation
│   ├── config/              ✅ Settings, URLs, Celery, WSGI
│   └── templates/reports/   ✅ quarterly_report.html, annual_report.html
├── frontend/src/
│   ├── app/(auth)/login/    ✅ Login page
│   ├── app/(dashboard)/     ✅ Dashboard, Analysis, Reports, Assistant, Data-Entry
│   ├── components/          ✅ Charts (ECharts), Layout, UI, Chat
│   ├── lib/                 ✅ API client (Axios), utils, auth
│   ├── hooks/               ✅ useApi
│   └── types/               ✅ TypeScript interfaces
├── nginx/                   ✅ Reverse proxy config
└── docker-compose.yml       ✅ Full stack orchestration
```

---

## Próximos Passos

1. ~~Corrigir alerta GitGuardian (credenciais no entrypoint.sh)~~ ✅
2. ~~Adicionar dependências em falta ao `requirements.txt`~~ ✅
3. ~~Corrigir bug do comparative market-share mapping~~ ✅
4. ~~Corrigir polling leak na geração de relatórios~~ ✅
5. ~~Limpar imports não usados e API calls redundantes~~ ✅
6. ~~Melhorar tratamento de erros (toast notifications)~~ ✅
7. ~~Actualizar README (remover credenciais, documentar fases 2-5)~~ ✅
8. Testar fluxo completo com Docker
9. Preparar dados de teste / importar dados históricos 2018-2023
10. Adicionar testes unitários (backend) e E2E (Playwright)
11. Configurar deploy de produção (Vercel ou VPS)

---

*Última actualização: 24 Mar 2026*
