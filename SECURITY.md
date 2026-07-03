# 🔒 Política de Segurança - Observatório ARN

## ⚠️ IMPORTANTE: Gerenciamento de Credenciais

### ❌ NUNCA FAÇA:
- Hardcode credenciais diretamente no código
- Commite arquivos contendo senhas, tokens ou chaves API
- Compartilhe credenciais via chat, email ou documentos

### ✅ SEMPRE FAÇA:
- Use variáveis de ambiente para todas as credenciais
- Mantenha o arquivo `.env` no `.gitignore`
- Use senhas de aplicativo para serviços Gmail/Google

## 📋 Configuração Segura

### 1. Arquivo .env (LOCAL APENAS)
```bash
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@arn.gw
EMAIL_HOST_PASSWORD=sua_senha_app_google

# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anonima
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role

# Google OAuth (se necessário)
GOOGLE_CLIENT_ID=seu_client_id
GOOGLE_CLIENT_SECRET=seu_client_secret
```

### 2. Senhas de App Google
Para Gmail/Google Workspace:
1. Ative 2FA na conta Google
2. Vá em "Senhas de app" nas configurações de segurança
3. Gere uma senha específica para o Observatório ARN
4. Use essa senha no `EMAIL_HOST_PASSWORD`

### 3. Variáveis de Produção
No servidor de produção, configure as variáveis via:
- Variáveis de ambiente do sistema
- Docker secrets
- Kubernetes secrets
- Serviços de configuração seguros

## 🚨 Em Caso de Vazamento

### Ação Imediata:
1. **Revogar/Alterar** todas as credenciais expostas
2. **Remover** do histórico Git com `git reset` ou `git rebase`
3. **Verificar logs** de acesso suspeito
4. **Notificar** a equipe de TI

### Comandos de Emergência:
```bash
# Remover último commit com credenciais
git reset --hard HEAD~1

# Remover arquivo específico do histórico
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch arquivo_com_credenciais.py' \
--prune-empty --tag-name-filter cat -- --all

# Forçar push após limpeza
git push origin --force --all
```

## 📝 Arquivos Sensíveis Bloqueados

O `.gitignore` está configurado para bloquear:
- `test_email.py`
- `*_credentials.py`
- `*_secrets.py`
- `*_keys.py`
- Todos os arquivos `test_*.py`

## 🔍 Ferramentas de Verificação

### Pre-commit Hook
```bash
# Instalar git-secrets
pip install git-secrets

# Configurar para detectar credenciais
git secrets --install
git secrets --register-aws
```

### Verificação Manual
```bash
# Buscar possíveis credenciais antes do commit
grep -r "password\|secret\|key\|token" --exclude-dir=.git --exclude-dir=venv .
```

## 📞 Contato de Segurança

Em caso de incidentes de segurança:
- **Email**: security@arn.gw
- **Telefone**: +245 XXX XXXX
- **Urgente**: Contatar diretamente a equipe de TI

## 📚 Recursos Adicionais

- [OWASP Security Guidelines](https://owasp.org/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)

---
**Última atualização**: 29/05/2025  
**Versão**: 1.0 