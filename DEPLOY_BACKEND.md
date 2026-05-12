# Deploy do Backend Django

## Onde fica cada parte

- Frontend Next.js: Vercel.
- Backend Django API: Render, como Web Service Docker.
- Base de dados: PostgreSQL no Render, ou outro PostgreSQL externo.
- Ficheiros media: storage S3 compatível quando o serviço for usado em produção real.

O browser dos utilizadores nunca deve tentar ligar a `localhost:8000`. Depois do backend estar publicado, a Vercel deve usar o URL público do backend.

## Deploy no Render

1. No Render, criar um Blueprint a partir do repositório GitHub.
2. O Render vai detectar `render.yaml` na raiz do repo.
3. Criar o serviço `observatorio-arn-backend` e a base `observatorio-arn-db`.
4. Preencher as variáveis marcadas como secretas no Render:
   - `FRONTEND_URL`: URL do frontend na Vercel, por exemplo `https://observatorio-arn.vercel.app`
   - `CORS_ALLOWED_ORIGINS`: mesmo valor do `FRONTEND_URL`
   - `CSRF_TRUSTED_ORIGINS`: mesmo valor do `FRONTEND_URL`
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL`
   - `DJANGO_SUPERUSER_PASSWORD`
   - `GEMINI_API_KEY`, se o assistente IA for usado
5. No frontend da Vercel, definir:
   - `NEXT_PUBLIC_API_URL=https://observatorio-arn-backend.onrender.com/api/v1`
6. Fazer redeploy do frontend na Vercel.

## Porque os utilizadores criados no PC não entram noutros PCs

Os utilizadores ficam gravados na base de dados onde foram criados.

Se crias utilizadores no teu PC, eles ficam na base local. Outro PC, ou o frontend na Vercel, só vai conseguir usar esses utilizadores se estiver a apontar para o mesmo backend e a mesma base de dados.

Em produção, cria os utilizadores no backend publicado no Render. A partir daí todos os PCs entram pelo mesmo frontend da Vercel e usam a mesma API.

## Media files

Uploads Excel e relatórios PDF/Excel/DOCX não devem depender do disco local do servidor em produção.

Para usar S3, Cloudflare R2, Backblaze B2 ou outro storage compatível com S3, configurar no backend:

- `USE_S3_STORAGE=true`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_REGION_NAME`
- `AWS_S3_CUSTOM_DOMAIN`, opcional
- `AWS_QUERYSTRING_AUTH=true`

Enquanto `USE_S3_STORAGE=false`, o backend usa o filesystem local. Isto serve para testes e demos, mas não é a opção certa para produção duradoura.

## Relatórios

O `render.yaml` começa com:

- `REPORTS_GENERATE_SYNC=true`

Isto evita Redis e Celery no primeiro deploy. Para produção com muitos relatórios ou ficheiros grandes, adicionar Redis e um worker Celery separado.
