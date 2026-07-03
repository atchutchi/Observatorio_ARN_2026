# 🔧 Scripts de Manutenção - Observatório ARN

Scripts úteis para manutenção e auditoria do projeto.

---

## 📋 Scripts Disponíveis

### 1. audit_templates.py

**Descrição:** Audita todos os templates HTML do projeto verificando padrões e boas práticas.

**Uso:**
```bash
# Executar auditoria
python scripts/audit_templates.py

# Com ambiente virtual ativo
python scripts/audit_templates.py
```

**Verifica:**
- ✅ Presença de CSRF tokens em formulários
- ✅ Validação de erros consistente (if/for com mesmo campo)
- ✅ Classe `d-block` em `invalid-feedback`
- ✅ Atributo `for` em labels
- ✅ ARIA attributes em campos obrigatórios

**Output:**
```
==================================== RELATÓRIO DE AUDITORIA ====================================

📊 ESTATÍSTICAS GERAIS
Total de templates: 122
Templates com formulários: 13

🔍 PROBLEMAS ENCONTRADOS
✗ Críticos: 45
⚠ Avisos: 120
ℹ Informativos: 30

📋 DETALHES POR TIPO DE PROBLEMA
  ✗ CSRF Token Faltando: 0
  ✗ Validação Inconsistente: 45
  ⚠ invalid-feedback sem d-block: 80
  ⚠ Labels sem atributo for: 40
  ℹ Campos sem ARIA attributes: 30
```

**Exit Codes:**
- `0` - Nenhum problema encontrado
- `1` - Problemas encontrados

---

## 🚀 Como Usar

### Pré-requisitos

```bash
# Python 3.9+
python --version

# Estar no diretório raiz do projeto
cd /caminho/para/observatorio-arn
```

### Executar Auditoria

```bash
# Método 1: Direto
python scripts/audit_templates.py

# Método 2: Como módulo
python -m scripts.audit_templates

# Método 3: Tornar executável (Linux/Mac)
chmod +x scripts/audit_templates.py
./scripts/audit_templates.py
```

### Interpretar Resultados

#### Severidades

| Nível | Descrição | Ação |
|-------|-----------|------|
| 🔴 **Crítico** | Bugs que podem quebrar funcionalidade | Corrigir imediatamente |
| 🟡 **Aviso** | Problemas de padrão/acessibilidade | Corrigir em breve |
| 🔵 **Info** | Melhorias recomendadas | Corrigir quando possível |

#### Exemplos de Problemas

**Crítico - Validação Inconsistente:**
```django
❌ ANTES:
{% if form.campo_A.errors %}
    {% for error in form.campo_B.errors %}

✅ DEPOIS:
{% if form.campo_A.errors %}
    {% for error in form.campo_A.errors %}
```

**Aviso - invalid-feedback sem d-block:**
```html
❌ ANTES:
<div class="invalid-feedback">

✅ DEPOIS:
<div class="invalid-feedback d-block">
```

**Info - ARIA attributes:**
```html
❌ ANTES:
<input type="text" required>

✅ DEPOIS:
<input type="text" required aria-required="true">
```

---

## 📈 Integração CI/CD

### GitHub Actions

```yaml
name: Template Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run Template Audit
        run: python scripts/audit_templates.py
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/audit_templates.py
if [ $? -ne 0 ]; then
    echo "❌ Template audit failed. Please fix issues before committing."
    exit 1
fi
```

---

## 🔧 Desenvolvimento

### Adicionar Nova Verificação

Edite `scripts/audit_templates.py`:

```python
def check_nova_regra(self, content, filepath):
    """Descrição da nova regra"""
    # Implementação
    if problema_encontrado:
        self.issues[filepath].append({
            'type': 'nova_regra',
            'severity': 'warning',  # critical, warning, info
            'message': 'Descrição do problema'
        })
        return False
    return True
```

Adicione ao método `audit_template`:

```python
def audit_template(self, template_path):
    # ... código existente ...
    self.check_nova_regra(content, str(template_path))
```

---

## 📚 Recursos

- [TEMPLATES_STANDARDIZATION_PLAN.md](../TEMPLATES_STANDARDIZATION_PLAN.md) - Plano completo
- [TEMPLATES_AUDIT_SUMMARY.md](../TEMPLATES_AUDIT_SUMMARY.md) - Resumo da auditoria
- [Django Templates Best Practices](https://docs.djangoproject.com/en/4.2/ref/templates/)

---

## 🐛 Troubleshooting

### Erro: "No such file or directory"

**Causa:** Script não encontra templates

**Solução:**
```bash
# Certifique-se de estar no diretório raiz
pwd  # Deve mostrar .../observatorio-arn

# Execute o script
python scripts/audit_templates.py
```

### Erro: "UnicodeDecodeError"

**Causa:** Encoding de arquivo incorreto

**Solução:** Abra o arquivo problemático e salve com UTF-8

### Muitos problemas encontrados

**Solução:** Foque primeiro nos críticos, depois avisos, depois info

```bash
# Ver apenas críticos
python scripts/audit_templates.py | grep "✗"

# Ver apenas avisos
python scripts/audit_templates.py | grep "⚠"
```

---

## 📞 Suporte

Para questões sobre os scripts:
1. Consulte a documentação acima
2. Veja exemplos de correção em TEMPLATES_STANDARDIZATION_PLAN.md
3. Abra um issue no repositório

---

**Última Atualização:** 04 de Novembro de 2025  
**Versão:** 1.0

