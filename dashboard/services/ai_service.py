"""
Serviço de IA ARN - Assistente integrado aos dados
Integração com HuggingFace e DeepSeek API
"""
import re
import json
import time
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Max, Min, F
from django.utils import timezone

# Imports dos modelos de dados das outras apps
from questionarios.models import (
    EstacoesMoveisIndicador, AssinantesIndicador, ReceitasIndicador,
    TrafegoOriginadoIndicador, TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador, LBIIndicador,
    TrafegoInternetIndicador, InternetFixoIndicador,
    InvestimentoIndicador, EmpregoIndicador
)

from dashboard.models import ChatSession, ChatMessage, ARNQueryCache

class ARNAssistantService:
    """Assistente ARN Analytics - IA integrada aos dados"""
    
    # Mapeamento de intenções para palavras-chave
    INTENT_PATTERNS = {
        'consulta_assinantes': [
            r'\b(assinantes?|clientes?|utilizadores?|estações?|quantos?)\b',
            r'\b(número|total|quantidade)\s+(de\s+)?(assinantes?|clientes?)\b',
            r'\b(assinantes?\s+(activos?|móveis?|fixos?))\b'
        ],
        'analise_trafego': [
            r'\b(tráfego|trafego|chamadas?|minutos?|voz)\b',
            r'\b(volume\s+de\s+)?(chamadas?|tráfego)\b',
            r'\b(on-net|off-net|internacional)\b'
        ],
        'mobile_money': [
            r'\b(mobile\s+money|transferência|carregamento|levantamento)\b',
            r'\b(transações?\s+financeiras?)\b',
            r'\b(dinheiro\s+móvel)\b'
        ],
        'market_share': [
            r'\b(quota|market\s+share|percentagem|domínio|liderança)\b',
            r'\b(participação\s+no\s+mercado)\b',
            r'\b(maior\s+operadora|líder\s+do\s+mercado)\b'
        ],
        'receitas': [
            r'\b(receitas?|faturamento|volume\s+de\s+negócios|FCFA)\b',
            r'\b(lucros?|ganhos?|rendimentos?)\b'
        ],
        'investimentos': [
            r'\b(investimentos?|CAPEX|infraestrutura|gastos)\b',
            r'\b(aplicação\s+de\s+capital)\b'
        ],
        'comparacao_operadores': [
            r'\b(comparar|versus|vs|diferença|melhor|maior)\b',
            r'\b(TELECEL\s+(vs|versus|contra)\s+Orange)\b',
            r'\b(qual\s+é\s+(melhor|maior))\b'
        ],
        'tendencias': [
            r'\b(tendência|evolução|crescimento|queda|variação)\b',
            r'\b(como\s+evoluiu|está\s+crescendo)\b'
        ]
    }
    
    # Entidades reconhecidas
    ENTITIES = {
        'operadores': {
            'ORANGE': ['orange', 'orange bissau'],
            'TELECEL': ['telecel', 'telecel', 'antiga telecel']  # TELECEL é a antiga MTN
        },
        'periodos': {
            'pattern': r'\b(20\d{2}|último|este|próximo)\s*(ano|trimestre|mês)?\b',
            'anos': [2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'trimestres': [1, 2, 3, 4]
        },
        'metricas': {
            'assinantes': ['assinantes', 'clientes', 'utilizadores'],
            'receitas': ['receitas', 'faturamento', 'fcfa'],
            'trafego': ['tráfego', 'chamadas', 'minutos'],
            'investimento': ['investimento', 'capex', 'gastos']
        }
    }
    
    def __init__(self):
        self.current_year = timezone.now().year
        
    def processar_mensagem(self, mensagem, usuario, sessao_id=None):
        """Processa mensagem do usuário e retorna resposta estruturada"""
        start_time = time.time()
        
        # Obter ou criar sessão
        if sessao_id:
            try:
                sessao = ChatSession.objects.get(id=sessao_id, usuario=usuario, ativa=True)
            except ChatSession.DoesNotExist:
                sessao = self.criar_nova_sessao(usuario)
        else:
            sessao = self.criar_nova_sessao(usuario)
        
        # Salvar mensagem do usuário
        user_message = ChatMessage.objects.create(
            sessao=sessao,
            tipo='user',
            mensagem=mensagem
        )
        
        # Detectar intenção
        intencao, confianca = self.detectar_intencao(mensagem)
        
        # Extrair entidades
        entidades = self.extrair_entidades(mensagem)
        
        # Buscar dados baseado na intenção
        dados = self.buscar_dados_contextuais(intencao, entidades)
        
        # Gerar resposta
        resposta = self.gerar_resposta(intencao, entidades, dados)
        
        # Calcular tempo de resposta
        tempo_resposta = time.time() - start_time
        
        # Salvar resposta do bot
        bot_message = ChatMessage.objects.create(
            sessao=sessao,
            tipo='bot',
            mensagem=resposta['texto'],
            intencao_detectada=intencao,
            confianca=confianca,
            dados_resposta=dados,
            tempo_resposta=tempo_resposta
        )
        
        return {
            'resposta': resposta['texto'],
            'dados': dados,
            'graficos': resposta.get('graficos', []),
            'sugestoes': resposta.get('sugestoes', []),
            'intencao': intencao,
            'confianca': confianca,
            'sessao_id': str(sessao.id),
            'tempo_resposta': tempo_resposta
        }
    
    def detectar_intencao(self, mensagem):
        """Detecta a intenção da mensagem usando patterns regex"""
        mensagem_lower = mensagem.lower()
        
        scores = {}
        
        for intencao, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, mensagem_lower)
                score += len(matches)
            
            if score > 0:
                scores[intencao] = score
        
        if not scores:
            return 'nao_entendido', 0.0
        
        # Retorna a intenção com maior score
        melhor_intencao = max(scores, key=scores.get)
        confianca = min(scores[melhor_intencao] / 3.0, 1.0)  # Normalizar confiança
        
        return melhor_intencao, confianca
    
    def extrair_entidades(self, mensagem):
        """Extrai entidades da mensagem"""
        entidades = {}
        mensagem_lower = mensagem.lower()
        
        # Detectar operadoras
        for operadora, aliases in self.ENTITIES['operadores'].items():
            for alias in aliases:
                if alias in mensagem_lower:
                    entidades['operadora'] = operadora
                    break
        
        # Detectar anos
        ano_match = re.search(r'\b(20\d{2})\b', mensagem)
        if ano_match:
            entidades['ano'] = int(ano_match.group(1))
        elif 'último ano' in mensagem_lower or 'ano passado' in mensagem_lower:
            entidades['ano'] = self.current_year - 1
        elif 'este ano' in mensagem_lower:
            entidades['ano'] = self.current_year
        
        # Detectar trimestres
        trimestre_match = re.search(r'\b([1-4])º?\s*trimestre\b', mensagem_lower)
        if trimestre_match:
            entidades['trimestre'] = int(trimestre_match.group(1))
        
        return entidades
    
    def buscar_dados_contextuais(self, intencao, entidades):
        """Busca dados baseado na intenção e entidades"""
        
        # Verificar cache primeiro
        cache_key = f"{intencao}:{json.dumps(entidades, sort_keys=True)}"
        cached_result = ARNQueryCache.get_cached(cache_key)
        
        if cached_result:
            return cached_result
        
        dados = {}
        
        try:
            if intencao == 'consulta_assinantes':
                dados = self.consultar_assinantes(entidades)
            elif intencao == 'analise_trafego':
                dados = self.consultar_trafego(entidades)
            elif intencao == 'market_share':
                dados = self.calcular_market_share(entidades)
            elif intencao == 'receitas':
                dados = self.consultar_receitas(entidades)
            elif intencao == 'investimentos':
                dados = self.consultar_investimentos(entidades)
            elif intencao == 'comparacao_operadores':
                dados = self.comparar_operadores(entidades)
            elif intencao == 'tendencias':
                dados = self.analisar_tendencias(entidades)
            else:
                dados = {'tipo': 'informativo', 'dados': {}}
                
        except Exception as e:
            dados = {'erro': str(e), 'tipo': 'erro'}
        
        # Salvar no cache
        ARNQueryCache.set_cache(cache_key, dados, validade=1800)  # 30 minutos
        
        return dados
    
    def consultar_assinantes(self, entidades):
        """Consulta dados de assinantes"""
        ano = entidades.get('ano', self.current_year)
        operadora = entidades.get('operadora')
        
        queryset = AssinantesIndicador.objects.filter(ano=ano)
        
        if operadora:
            queryset = queryset.filter(operadora=operadora)
        
        # Agregações usando campos corretos
        totais = queryset.aggregate(
            total_pre_pago=Sum('assinantes_pre_pago'),
            total_pos_pago=Sum('assinantes_pos_pago'),
            total_fixo=Sum('assinantes_fixo'),
            total_internet_movel=Sum('assinantes_internet_movel'),
            total_internet_fixa=Sum('assinantes_internet_fixa')
        )
        
        # Calcular total de assinantes
        total_assinantes = (
            (totais['total_pre_pago'] or 0) +
            (totais['total_pos_pago'] or 0) +
            (totais['total_fixo'] or 0) +
            (totais['total_internet_movel'] or 0) +
            (totais['total_internet_fixa'] or 0)
        )
        totais['total_assinantes'] = total_assinantes
        
        # Por operadora
        por_operadora = []
        for item in queryset.values('operadora').annotate(
            pre_pago=Sum('assinantes_pre_pago'),
            pos_pago=Sum('assinantes_pos_pago'),
            fixo=Sum('assinantes_fixo'),
            internet_movel=Sum('assinantes_internet_movel'),
            internet_fixa=Sum('assinantes_internet_fixa')
        ):
            total_operadora = (
                (item['pre_pago'] or 0) +
                (item['pos_pago'] or 0) +
                (item['fixo'] or 0) +
                (item['internet_movel'] or 0) +
                (item['internet_fixa'] or 0)
            )
            item['total'] = total_operadora
            por_operadora.append(item)
        
        # Calcular market share
        total_mercado = totais['total_assinantes'] or 0
        
        for item in por_operadora:
            if total_mercado > 0:
                item['market_share'] = round((item['total'] / total_mercado) * 100, 2)
            else:
                item['market_share'] = 0
        
        return {
            'tipo': 'assinantes',
            'ano': ano,
            'operadora_filtro': operadora,
            'totais': totais,
            'por_operadora': por_operadora,
            'total_mercado': total_mercado
        }
    
    def consultar_trafego(self, entidades):
        """Consulta dados de tráfego"""
        ano = entidades.get('ano', self.current_year)
        operadora = entidades.get('operadora')
        
        queryset = TrafegoOriginadoIndicador.objects.filter(ano=ano)
        
        if operadora:
            queryset = queryset.filter(operadora=operadora)
        
        # Agregações por tipo de tráfego
        trafego_data = queryset.aggregate(
            total_on_net=Sum('chamadas_on_net'),
            total_off_net=Sum('chamadas_off_net'),
            total_internacional=Sum('chamadas_internacionais')
        )
        
        # Por operadora
        por_operadora = list(queryset.values('operadora').annotate(
            on_net=Sum('chamadas_on_net'),
            off_net=Sum('chamadas_off_net'),
            internacional=Sum('chamadas_internacionais')
        ))
        
        # Calcular percentuais
        total_trafego = sum(trafego_data.values()) or 1
        percentuais = {
            'on_net': round((trafego_data['total_on_net'] or 0) / total_trafego * 100, 1),
            'off_net': round((trafego_data['total_off_net'] or 0) / total_trafego * 100, 1),
            'internacional': round((trafego_data['total_internacional'] or 0) / total_trafego * 100, 1)
        }
        
        return {
            'tipo': 'trafego',
            'ano': ano,
            'operadora_filtro': operadora,
            'totais': trafego_data,
            'percentuais': percentuais,
            'por_operadora': por_operadora,
            'total_trafego': total_trafego
        }
    
    def calcular_market_share(self, entidades):
        """Calcula market share das operadoras"""
        ano = entidades.get('ano', self.current_year)
        
        assinantes_data = AssinantesIndicador.objects.filter(ano=ano)
        
        # Total do mercado
        total_mercado = assinantes_data.aggregate(
            total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
        )['total'] or 0
        
        # Por operadora
        market_share = []
        
        for operadora in ['ORANGE', 'TELECEL']:
            operadora_total = assinantes_data.filter(operadora=operadora).aggregate(
                total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
            )['total'] or 0
            
            if total_mercado > 0:
                percentual = round((operadora_total / total_mercado) * 100, 2)
            else:
                percentual = 0
            
            market_share.append({
                'operadora': operadora,
                'assinantes': operadora_total,
                'percentual': percentual
            })
        
        # Ordenar por percentual
        market_share.sort(key=lambda x: x['percentual'], reverse=True)
        
        return {
            'tipo': 'market_share',
            'ano': ano,
            'total_mercado': total_mercado,
            'distribuicao': market_share,
            'lider': market_share[0] if market_share else None
        }
    
    def consultar_receitas(self, entidades):
        """Consulta dados de receitas"""
        ano = entidades.get('ano', self.current_year)
        operadora = entidades.get('operadora')
        
        queryset = ReceitasIndicador.objects.filter(ano=ano)
        
        if operadora:
            queryset = queryset.filter(operadora=operadora)
        
        # Totais
        totais = queryset.aggregate(
            total_receitas=Sum('receita_total'),
            media_trimestral=Avg('receita_total')
        )
        
        # Por operadora
        por_operadora = list(queryset.values('operadora').annotate(
            total=Sum('receita_total'),
            media=Avg('receita_total')
        ))
        
        # Calcular crescimento anual
        ano_anterior = ano - 1
        receitas_anteriores = ReceitasIndicador.objects.filter(ano=ano_anterior).aggregate(
            total=Sum('receita_total')
        )['total'] or 0
        
        crescimento = 0
        if receitas_anteriores > 0 and totais['total_receitas']:
            crescimento = round(
                ((totais['total_receitas'] - receitas_anteriores) / receitas_anteriores) * 100, 2
            )
        
        return {
            'tipo': 'receitas',
            'ano': ano,
            'operadora_filtro': operadora,
            'totais': totais,
            'por_operadora': por_operadora,
            'crescimento_anual': crescimento
        }
    
    def comparar_operadores(self, entidades):
        """Compara indicadores entre operadoras"""
        ano = entidades.get('ano', self.current_year)
        
        # Buscar dados de assinantes (usando campos corretos)
        def calcular_total_assinantes_operadora(operadora, ano):
            data = AssinantesIndicador.objects.filter(ano=ano, operadora=operadora).aggregate(
                pre_pago=Sum('assinantes_pre_pago'),
                pos_pago=Sum('assinantes_pos_pago'),
                fixo=Sum('assinantes_fixo'),
                internet_movel=Sum('assinantes_internet_movel'),
                internet_fixa=Sum('assinantes_internet_fixa')
            )
            return sum((data[k] or 0) for k in data.keys())
        
        assinantes_telecel = calcular_total_assinantes_operadora('TELECEL', ano)
        assinantes_orange = calcular_total_assinantes_operadora('ORANGE', ano)
        
        # Buscar dados de receitas
        receitas_telecel = ReceitasIndicador.objects.filter(
            ano=ano, operadora='TELECEL'
        ).aggregate(total=Sum('receita_total'))['total'] or 0
        
        receitas_orange = ReceitasIndicador.objects.filter(
            ano=ano, operadora='ORANGE'
        ).aggregate(total=Sum('receita_total'))['total'] or 0
        
        # Buscar dados de tráfego
        trafego_telecel = TrafegoOriginadoIndicador.objects.filter(
            ano=ano, operadora='TELECEL'
        ).aggregate(
            on_net=Sum('chamadas_on_net'),
            off_net=Sum('chamadas_off_net'),
            internacional=Sum('chamadas_internacionais')
        )
        trafego_telecel_total = sum((trafego_telecel[k] or 0) for k in trafego_telecel.keys())
        
        trafego_orange = TrafegoOriginadoIndicador.objects.filter(
            ano=ano, operadora='ORANGE'
        ).aggregate(
            on_net=Sum('chamadas_on_net'),
            off_net=Sum('chamadas_off_net'),
            internacional=Sum('chamadas_internacionais')
        )
        trafego_orange_total = sum((trafego_orange[k] or 0) for k in trafego_orange.keys())
        
        return {
            'tipo': 'comparacao',
            'ano': ano,
            'telecel': {
                'assinantes': assinantes_telecel,
                'receitas': receitas_telecel,
                'trafego': trafego_telecel_total
            },
            'orange': {
                'assinantes': assinantes_orange,
                'receitas': receitas_orange,
                'trafego': trafego_orange_total
            },
            'diferencas': {
                'assinantes': assinantes_orange - assinantes_telecel,
                'receitas': receitas_orange - receitas_telecel,
                'trafego': trafego_orange_total - trafego_telecel_total
            }
        }
    
    def gerar_resposta(self, intencao, entidades, dados):
        """Gera resposta baseada na intenção e dados"""
        
        if intencao == 'saudacao':
            return {
                'texto': "Olá! Sou o Assistente ARN Analytics. Posso ajudar você com dados sobre o mercado de telecomunicações da Guiné-Bissau. Pergunte sobre assinantes, receitas, tráfego ou market share!",
                'sugestoes': [
                    "Qual a quota de mercado da Orange?",
                    "Mostre os dados de assinantes de 2023",
                    "Compare TELECEL e Orange em receitas",
                    "Como evoluiu o tráfego nos últimos anos?"
                ]
            }
        
        elif intencao == 'consulta_assinantes':
            return self.resposta_assinantes(dados, entidades)
        
        elif intencao == 'analise_trafego':
            return self.resposta_trafego(dados, entidades)
        
        elif intencao == 'market_share':
            return self.resposta_market_share(dados, entidades)
        
        elif intencao == 'receitas':
            return self.resposta_receitas(dados, entidades)
        
        elif intencao == 'comparacao_operadores':
            return self.resposta_comparacao(dados, entidades)
        
        elif intencao == 'nao_entendido':
            return {
                'texto': "Desculpe, não entendi sua pergunta. Posso ajudar com informações sobre:\n\n• Assinantes e estações móveis\n• Receitas e faturamento\n• Tráfego de voz e dados\n• Market share das operadoras\n• Comparações entre operadoras\n\nTente reformular sua pergunta.",
                'sugestoes': [
                    "Quantos assinantes tem a MTN?",
                    "Qual a receita total de 2023?",
                    "Compare o tráfego da Orange e TELECEL",
                    "Mostre o market share por operadora"
                ]
            }
        
        return {
            'texto': "Processando sua solicitação...",
            'dados': dados
        }
    
    def resposta_assinantes(self, dados, entidades):
        """Gera resposta para consultas de assinantes"""
        if dados.get('erro'):
            return {'texto': f"Erro ao consultar dados: {dados['erro']}"}
        
        ano = dados.get('ano', self.current_year)
        total = dados.get('totais', {}).get('total_assinantes', 0)
        operadora_filtro = dados.get('operadora_filtro')
        
        if operadora_filtro:
            operadora_data = next(
                (item for item in dados.get('por_operadora', []) if item['operadora'] == operadora_filtro),
                None
            )
            
            if operadora_data:
                texto = f"Em {ano}, a {operadora_filtro} tinha {operadora_data['total']:,} assinantes, representando {operadora_data['market_share']}% do mercado."
            else:
                texto = f"Não encontrei dados de assinantes para a {operadora_filtro} em {ano}."
        else:
            texto = f"Em {ano}, o mercado de telecomunicações da Guiné-Bissau tinha {total:,} assinantes no total."
            
            if dados.get('por_operadora'):
                texto += "\n\nDistribuição por operadora:"
                for item in dados['por_operadora']:
                    texto += f"\n• {item['operadora']}: {item['total']:,} assinantes ({item['market_share']}%)"
        
        return {
            'texto': texto,
            'graficos': [
                {
                    'tipo': 'pie',
                    'titulo': f'Market Share - Assinantes {ano}',
                    'dados': dados.get('por_operadora', [])
                }
            ],
            'sugestoes': [
                f"Compare assinantes entre operadoras em {ano}",
                f"Mostre a evolução de assinantes",
                f"Qual operadora cresceu mais em {ano}?"
            ]
        }
    
    def resposta_market_share(self, dados, entidades):
        """Gera resposta para consultas de market share"""
        if dados.get('erro'):
            return {'texto': f"Erro ao consultar market share: {dados['erro']}"}
        
        ano = dados.get('ano', self.current_year)
        total_mercado = dados.get('total_mercado', 0)
        distribuicao = dados.get('distribuicao', [])
        lider = dados.get('lider')
        
        if not distribuicao:
            return {'texto': f"Não encontrei dados de market share para {ano}."}
        
        texto = f"Market Share do mercado de telecomunicações em {ano}:\n\n"
        
        for item in distribuicao:
            emoji = "🥇" if item == lider else "📊"
            texto += f"{emoji} {item['operadora']}: {item['percentual']}% ({item['assinantes']:,} assinantes)\n"
        
        if lider:
            texto += f"\n🏆 A {lider['operadora']} é líder de mercado com {lider['percentual']}% de quota."
        
        return {
            'texto': texto,
            'graficos': [
                {
                    'tipo': 'doughnut',
                    'titulo': f'Market Share {ano}',
                    'dados': distribuicao
                }
            ]
        }
    
    def resposta_trafego(self, dados, entidades):
        """Gera resposta para consultas de tráfego"""
        if dados.get('erro'):
            return {'texto': f"Erro ao consultar tráfego: {dados['erro']}"}
        
        ano = dados.get('ano', self.current_year)
        totais = dados.get('totais', {})
        percentuais = dados.get('percentuais', {})
        
        total_trafego = dados.get('total_trafego', 0)
        
        texto = f"Análise de tráfego de voz em {ano}:\n\n"
        texto += f"📞 Volume total: {total_trafego:,} minutos\n\n"
        texto += "Distribuição por tipo:\n"
        texto += f"• On-Net: {percentuais.get('on_net', 0)}% ({totais.get('total_on_net', 0):,} min)\n"
        texto += f"• Off-Net: {percentuais.get('off_net', 0)}% ({totais.get('total_off_net', 0):,} min)\n"
        texto += f"• Internacional: {percentuais.get('internacional', 0)}% ({totais.get('total_internacional', 0):,} min)\n"
        
        return {
            'texto': texto,
            'graficos': [
                {
                    'tipo': 'bar',
                    'titulo': f'Distribuição de Tráfego {ano}',
                    'dados': [
                        {'label': 'On-Net', 'value': totais.get('total_on_net', 0)},
                        {'label': 'Off-Net', 'value': totais.get('total_off_net', 0)},
                        {'label': 'Internacional', 'value': totais.get('total_internacional', 0)}
                    ]
                }
            ]
        }
    
    def resposta_receitas(self, dados, entidades):
        """Gera resposta para consultas de receitas"""
        if dados.get('erro'):
            return {'texto': f"Erro ao consultar receitas: {dados['erro']}"}
        
        ano = dados.get('ano', self.current_year)
        totais = dados.get('totais', {})
        crescimento = dados.get('crescimento_anual', 0)
        
        total_receitas = totais.get('total_receitas', 0)
        
        texto = f"Receitas do setor de telecomunicações em {ano}:\n\n"
        texto += f"💰 Volume total: {total_receitas/1000000:,.0f} milhões FCFA\n"
        
        if crescimento != 0:
            emoji = "📈" if crescimento > 0 else "📉"
            texto += f"{emoji} Crescimento anual: {crescimento:+.1f}%\n"
        
        if dados.get('por_operadora'):
            texto += "\nReceitas por operadora:\n"
            for item in dados['por_operadora']:
                texto += f"• {item['operadora']}: {item['total']/1000000:,.0f} milhões FCFA\n"
        
        return {
            'texto': texto,
            'graficos': [
                {
                    'tipo': 'bar',
                    'titulo': f'Receitas por Operadora {ano}',
                    'dados': dados.get('por_operadora', [])
                }
            ]
        }
    
    def resposta_comparacao(self, dados, entidades):
        """Gera resposta para comparação entre operadoras"""
        if dados.get('erro'):
            return {'texto': f"Erro na comparação: {dados['erro']}"}
        
        ano = dados.get('ano', self.current_year)
        telecel = dados.get('telecel', {})
        orange = dados.get('orange', {})
        diferencas = dados.get('diferencas', {})
        
        texto = f"Comparação TELECEL vs Orange em {ano}:\n\n"
        
        # Assinantes
        texto += f"👥 Assinantes:\n"
        texto += f"• TELECEL: {telecel.get('assinantes', 0):,}\n"
        texto += f"• Orange: {orange.get('assinantes', 0):,}\n"
        
        diff_assinantes = diferencas.get('assinantes', 0)
        if diff_assinantes > 0:
            texto += f"📊 Orange tem {diff_assinantes:,} assinantes a mais\n\n"
        elif diff_assinantes < 0:
            texto += f"📊 TELECEL tem {abs(diff_assinantes):,} assinantes a mais\n\n"
        
        # Receitas
        texto += f"💰 Receitas:\n"
        texto += f"• TELECEL: {telecel.get('receitas', 0)/1000000:,.0f} M FCFA\n"
        texto += f"• Orange: {orange.get('receitas', 0)/1000000:,.0f} M FCFA\n"
        
        return {
            'texto': texto,
            'graficos': [
                {
                    'tipo': 'comparison',
                    'titulo': f'TELECEL vs Orange {ano}',
                    'dados': {
                        'telecel': telecel,
                        'orange': orange
                    }
                }
            ]
        }
    
    def criar_nova_sessao(self, usuario):
        """Cria nova sessão de chat"""
        return ChatSession.objects.create(
            usuario=usuario,
            contexto={'inicio': timezone.now().isoformat()}
        )
    
    def obter_historico_sessao(self, sessao_id, limite=20):
        """Obtém histórico de mensagens da sessão"""
        try:
            sessao = ChatSession.objects.get(id=sessao_id)
            mensagens = sessao.mensagens.order_by('timestamp')[:limite]
            
            return [
                {
                    'tipo': msg.tipo,
                    'mensagem': msg.mensagem,
                    'timestamp': msg.timestamp.isoformat(),
                    'intencao': msg.intencao_detectada,
                    'confianca': msg.confianca
                }
                for msg in mensagens
            ]
        except ChatSession.DoesNotExist:
            return []
