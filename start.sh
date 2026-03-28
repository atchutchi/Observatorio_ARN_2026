#!/bin/bash
# ============================================================
# Observatório Telecom GB — Script de Arranque Local
# ============================================================
# Uso:  ./start.sh          (arrancar backend + frontend)
#       ./start.sh backend   (só backend)
#       ./start.sh frontend  (só frontend)
#       ./start.sh setup     (primeira vez: instala tudo + migra + seed)
#       ./start.sh stop      (para todos os servidores)
# ============================================================

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_PYTHON="$BACKEND_DIR/venv/bin/python"
VENV_PIP="$BACKEND_DIR/venv/bin/pip"
PID_DIR="$ROOT_DIR/.pids"

export DJANGO_SETTINGS_MODULE=config.settings.development
export USE_SQLITE=true

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$PID_DIR"

stop_servers() {
    echo -e "${YELLOW}Parando servidores...${NC}"
    if [ -f "$PID_DIR/backend.pid" ]; then
        kill "$(cat "$PID_DIR/backend.pid")" 2>/dev/null && echo -e "${GREEN}Backend parado${NC}"
        rm -f "$PID_DIR/backend.pid"
    fi
    if [ -f "$PID_DIR/frontend.pid" ]; then
        kill "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null && echo -e "${GREEN}Frontend parado${NC}"
        rm -f "$PID_DIR/frontend.pid"
    fi
    echo -e "${GREEN}Todos os servidores parados.${NC}"
}

setup() {
    echo -e "${BLUE}=== SETUP INICIAL ===${NC}"

    if [ ! -d "$BACKEND_DIR/venv" ]; then
        echo -e "${YELLOW}Criando virtual environment...${NC}"
        python3 -m venv "$BACKEND_DIR/venv"
    fi

    echo -e "${YELLOW}Instalando dependências backend...${NC}"
    "$VENV_PIP" install -r "$BACKEND_DIR/requirements.txt" 2>&1 | tail -3

    echo -e "${YELLOW}Executando migrações...${NC}"
    cd "$BACKEND_DIR" && "$VENV_PYTHON" manage.py migrate --noinput 2>&1 | tail -5

    echo -e "${YELLOW}Carregando dados de referência...${NC}"
    cd "$BACKEND_DIR" && "$VENV_PYTHON" manage.py seed_data 2>&1 | tail -3

    echo -e "${YELLOW}Importando dados KPI (2024 + 2018)...${NC}"
    cd "$BACKEND_DIR" && "$VENV_PYTHON" manage.py import_kpi_json --data-dir data/kpi_2024 2>&1 | tail -3
    cd "$BACKEND_DIR" && "$VENV_PYTHON" manage.py import_kpi_json --data-dir data/kpi_2018 2>&1 | tail -3

    echo -e "${YELLOW}Criando superuser (admin/admin123)...${NC}"
    cd "$BACKEND_DIR" && "$VENV_PYTHON" -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
os.environ['USE_SQLITE'] = 'true'
django.setup()
from apps.accounts.models import User
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@arn.gw', 'admin123')
    u.role = 'admin_arn'
    u.first_name = 'Administrador'
    u.last_name = 'ARN'
    u.save()
    print('Superuser admin criado')
else:
    print('Superuser admin já existe')
" 2>&1

    echo -e "${YELLOW}Instalando dependências frontend...${NC}"
    cd "$FRONTEND_DIR" && npm install 2>&1 | tail -3

    echo -e "${GREEN}=== SETUP COMPLETO ===${NC}"
}

start_backend() {
    echo -e "${BLUE}Arrancando backend Django (http://localhost:8000)...${NC}"
    cd "$BACKEND_DIR" && "$VENV_PYTHON" manage.py runserver 0.0.0.0:8000 &
    echo $! > "$PID_DIR/backend.pid"
    sleep 2
    echo -e "${GREEN}Backend a correr! PID: $(cat "$PID_DIR/backend.pid")${NC}"
}

start_frontend() {
    echo -e "${BLUE}Arrancando frontend Next.js (http://localhost:3000)...${NC}"
    cd "$FRONTEND_DIR" && npm run dev &
    echo $! > "$PID_DIR/frontend.pid"
    sleep 3
    echo -e "${GREEN}Frontend a correr! PID: $(cat "$PID_DIR/frontend.pid")${NC}"
}

case "${1:-all}" in
    setup)
        setup
        ;;
    backend)
        stop_servers
        start_backend
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  Backend:  http://localhost:8000${NC}"
        echo -e "${GREEN}  Admin:    http://localhost:8000/admin${NC}"
        echo -e "${GREEN}  API:      http://localhost:8000/api/v1/${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${YELLOW}  Ctrl+C para parar${NC}"
        wait
        ;;
    frontend)
        stop_servers
        start_frontend
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  Frontend: http://localhost:3000${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${YELLOW}  Ctrl+C para parar${NC}"
        wait
        ;;
    stop)
        stop_servers
        ;;
    all|"")
        stop_servers
        echo ""
        echo -e "${BLUE}=== Observatório Telecom GB ===${NC}"
        echo ""
        start_backend
        start_frontend
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  Frontend: http://localhost:3000${NC}"
        echo -e "${GREEN}  Backend:  http://localhost:8000${NC}"
        echo -e "${GREEN}  Admin:    http://localhost:8000/admin${NC}"
        echo -e "${GREEN}  API:      http://localhost:8000/api/v1/${NC}"
        echo -e "${GREEN}----------------------------------------${NC}"
        echo -e "${GREEN}  Login:    admin / admin123${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${YELLOW}  Ctrl+C para parar tudo${NC}"
        trap stop_servers EXIT INT TERM
        wait
        ;;
    *)
        echo "Uso: $0 {setup|backend|frontend|stop|all}"
        exit 1
        ;;
esac
