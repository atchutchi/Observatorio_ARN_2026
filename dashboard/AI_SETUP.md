# 🤖 Configuração do Assistente ARN Analytics

## 🎯 **APIs de IA Suportadas**

### **1. 🤗 HuggingFace (Gratuito)**
- **Website**: https://huggingface.co/
- **Obter Token**: https://huggingface.co/settings/tokens
- **Variável**: `HUGGINGFACE_API_TOKEN=hf_sua_chave_aqui`

**Modelos Usados:**
- `microsoft/DialoGPT-medium` - Conversação
- `neuralmind/bert-base-portuguese-cased` - Classificação PT-BR
- `pierreguillou/bert-base-cased-pt-ner` - Entidades PT-BR

### **2. 🧠 DeepSeek API (Pago/Free Tier)**
- **Website**: https://platform.deepseek.com/
- **Documentação**: https://api-docs.deepseek.com/
- **Obter Chave**: https://platform.deepseek.com/api_keys
- **Variável**: `DEEPSEEK_API_KEY=sk-sua_chave_deepseek_aqui`

**Modelos Disponíveis:**
- `deepseek-chat` - Conversação geral
- `deepseek-reasoner` - Raciocínio avançado (R1)

---

## ⚙️ **Configuração no .env**

```bash
# Adicione ao seu arquivo .env:

# HuggingFace (Gratuito)
HUGGINGFACE_API_TOKEN=hf_sua_chave_aqui

# DeepSeek (Opcional)
DEEPSEEK_API_KEY=sk-sua_chave_deepseek_aqui
```

---

## 🚀 **Como Funciona o Sistema**

### **🔄 Fluxo de Processamento:**

1. **Usuário faz pergunta** sobre dados de telecomunicações
2. **Detectar intenção** usando patterns regex + HuggingFace
3. **Extrair entidades** (operadora, ano, trimestre)
4. **Buscar dados** nos modelos do Django (questionarios.models)
5. **Processar com IA** (HuggingFace ou DeepSeek)
6. **Gerar resposta** com dados estruturados + gráficos
7. **Cache** resultado para otimização

### **📊 Dados Integrados:**
- **Assinantes** (EstacoesMoveisIndicador, AssinantesIndicador)
- **Receitas** (ReceitasIndicador)
- **Tráfego** (TrafegoOriginadoIndicador, TrafegoTerminadoIndicador)
- **Investimentos** (InvestimentoIndicador)
- **Emprego** (EmpregoIndicador)
- **Internet** (LBIIndicador, TrafegoInternetIndicador)

---

## 💡 **Exemplos de Perguntas**

### **📊 Market Share:**
- "Qual a quota de mercado da Orange?"
- "Quem é líder do mercado em 2023?"
- "Mostre o market share por operadora"

### **📞 Tráfego:**
- "Volume de tráfego da TELECEL em 2023"
- "Análise de tráfego on-net vs off-net"
- "Como evoluiu o tráfego internacional?"

### **💰 Receitas:**
- "Receitas totais do setor em 2023"
- "Compare receitas TELECEL vs Orange"
- "Crescimento de receitas ano a ano"

### **⚖️ Comparações:**
- "Compare TELECEL e Orange"
- "Diferença de assinantes entre operadoras"
- "Qual operadora tem mais receitas?"

### **📈 Tendências:**
- "Como cresceu o mercado nos últimos 5 anos?"
- "Tendência de assinantes por trimestre"
- "Projeção para o próximo ano"

---

## 🛠 **Funcionalidades Técnicas**

### **🎯 Detecção de Intenções:**
```python
# Patterns regex para cada tipo de consulta
'consulta_assinantes': [
    r'\b(assinantes?|clientes?|utilizadores?)\b',
    r'\b(número|total|quantidade)\s+(de\s+)?(assinantes?)\b'
]
```

### **🔍 Extração de Entidades:**
```python
# Entidades reconhecidas automaticamente
operadoras: ['TELECEL', 'ORANGE', 'TELECEL']
anos: [2019, 2020, 2021, 2022, 2023, 2024, 2025]
trimestres: [1, 2, 3, 4]
```

### **💾 Sistema de Cache:**
- Cache automático de consultas frequentes
- TTL configurável (padrão: 30 minutos)
- Otimização de performance

### **📈 Geração de Gráficos:**
- Chart.js integrado
- Gráficos automáticos baseados nos dados
- Tipos: pizza, barras, linha, comparação

---

## 🔧 **Instalação e Configuração**

### **1. Instalar Dependências:**
```bash
pip install transformers torch requests
pip install huggingface_hub
```

### **2. Configurar Chaves:**
```bash
# No arquivo .env
HUGGINGFACE_API_TOKEN=hf_xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
```

### **3. Aplicar Migrations:**
```bash
python manage.py makemigrations dashboard
python manage.py migrate dashboard
```

### **4. Inicializar Intenções (Opcional):**
```bash
python manage.py populate_chat_intents
```

---

## 🎭 **Personalização**

### **Adicionar Nova Intenção:**
1. Adicionar pattern em `ARNAssistantService.INTENT_PATTERNS`
2. Criar método `consultar_nova_intencao()` em `ai_service.py`
3. Adicionar template de resposta em `gerar_resposta()`

### **Integrar Nova API de IA:**
1. Criar classe em `ai_integration.py`
2. Adicionar ao `AIOrchestrator`
3. Configurar fallbacks

---

## 🎉 **Resultado**

O **Assistente ARN Analytics** oferece:

✅ **IA Nativa** integrada aos dados reais  
✅ **Processamento em Português** otimizado  
✅ **Gráficos Automáticos** baseados nas consultas  
✅ **Cache Inteligente** para performance  
✅ **Múltiplas APIs** (HuggingFace + DeepSeek)  
✅ **Interface Binance** moderna e profissional  

**🚀 Um assistente de IA de nível enterprise para dados de telecomunicações!**
