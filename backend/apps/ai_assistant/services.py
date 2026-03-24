import json
import logging
from datetime import datetime

from django.conf import settings
from apps.dashboards.services import DashboardService
from apps.operators.models import Operator
from apps.indicators.models import IndicatorCategory

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é o assistente IA do Observatório de Telecomunicações da Guiné-Bissau, gerido pela ARN (Autoridade Reguladora Nacional).

CONTEXTO DO MERCADO:
- País: Guiné-Bissau
- Moeda: F CFA (Franco CFA da África Ocidental)
- População de referência: ~2,07 milhões
- Regulador: ARN

OPERADORES:
- Telecel (anteriormente MTN) — operador terrestre completo (voz, SMS, dados, Mobile Money)
- Orange Bissau — operador terrestre completo (voz, SMS, dados, Mobile Money)
- Starlink (SpaceX) — operador satélite/ISP (apenas internet fixa, LBI, receitas, emprego, investimento)

NOTA IMPORTANTE: A Starlink NÃO possui indicadores de voz, SMS, roaming ou Mobile Money.

11 CATEGORIAS DE INDICADORES:
1. Estações Móveis (Parque de Assinantes) — só Telecel/Orange
2. Tráfego Originado — só Telecel/Orange (dados parcial Starlink)
3. Tráfego Terminado — só Telecel/Orange
4. Tráfego Roaming Internacional — só Telecel/Orange
5. LBI (Largura de Banda Internacional) — todos
6. Internet Fixo (Assinantes) — todos
7. Internet Traffic (Volume) — todos
8. Tarifário de Voz — só Telecel/Orange
9. Receitas — todos (adaptado para Starlink)
10. Empregos — todos
11. Investimento — todos (adaptado para Starlink)

INSTRUÇÕES:
- Responda SEMPRE em português (Portugal)
- Use dados factuais quando disponíveis no contexto
- Formate números com separadores de milhar
- Se não tiver dados suficientes, diga claramente
- Seja conciso mas informativo
- Quando relevante, mencione variações percentuais e comparações"""


class GeminiAssistant:

    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')

    def _get_model(self):
        if not self.api_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model_name)
        except ImportError:
            logger.warning("google-generativeai not installed")
            return None
        except Exception as e:
            logger.error(f"Failed opening Gemini model: {e}")
            return None

    def build_context(self):
        current_year = datetime.now().year
        context_parts = []

        try:
            summary = DashboardService.get_summary(current_year)
            context_parts.append(f"DADOS RESUMO {current_year}:")
            context_parts.append(f"  Total assinantes móvel: {summary['total_subscribers']:,.0f}")
            context_parts.append(f"  Volume de negócios: {summary['total_revenue']:,.0f} FCFA")
            context_parts.append(f"  Tráfego de dados: {summary['total_data_traffic']:,.0f}")
            context_parts.append(f"  Taxa penetração: {summary['penetration_rate']}%")
            context_parts.append(f"  Variação assinantes: {summary['subscriber_change']}%")
        except Exception:
            context_parts.append(f"Dados de {current_year} não disponíveis.")

        try:
            operators = Operator.objects.filter(is_active=True)
            context_parts.append("\nOPERADORES ACTIVOS:")
            for op in operators:
                context_parts.append(f"  - {op.name} ({op.code}) — {op.operator_type.name}")
        except Exception:
            pass

        for market in ['mobile', 'fixed_internet', 'revenue']:
            try:
                shares = DashboardService.get_market_share(current_year, market=market)
                if shares:
                    market_labels = {'mobile': 'Móvel', 'fixed_internet': 'Internet Fixa', 'revenue': 'Receitas'}
                    context_parts.append(f"\nQUOTA DE MERCADO — {market_labels.get(market, market)}:")
                    for s in shares:
                        context_parts.append(f"  {s['operator_name']}: {s['share_pct']}% ({s['value']:,.0f})")
            except Exception:
                pass

        try:
            categories = IndicatorCategory.objects.all().order_by('order')
            context_parts.append("\nCATEGORIAS DISPONÍVEIS:")
            for cat in categories:
                cum = " (cumulativo)" if cat.is_cumulative else ""
                context_parts.append(f"  {cat.order}. {cat.name}{cum}")
        except Exception:
            pass

        return "\n".join(context_parts)

    def query(self, user_message, chat_history=None):
        model = self._get_model()

        if model is None:
            return self._fallback_response(user_message)

        context = self.build_context()
        full_prompt = f"{SYSTEM_PROMPT}\n\nDADOS ACTUAIS DO SISTEMA:\n{context}"

        try:
            messages = [{'role': 'user', 'parts': [full_prompt + "\n\nINÍCIO DA CONVERSA"]}]

            if chat_history:
                for msg in chat_history[-10:]:
                    role = 'user' if msg['role'] == 'user' else 'model'
                    messages.append({'role': role, 'parts': [msg['content']]})
            else:
                messages.append({'role': 'model', 'parts': ['Olá! Sou o assistente do Observatório de Telecomunicações da Guiné-Bissau. Como posso ajudar?']})

            messages.append({'role': 'user', 'parts': [user_message]})

            response = model.generate_content(messages)
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_response(user_message)

    def _fallback_response(self, user_message):
        context = self.build_context()
        msg_lower = user_message.lower()

        if any(w in msg_lower for w in ['assinante', 'subscriber', 'estações']):
            return f"Aqui estão os dados disponíveis sobre assinantes:\n\n{context}\n\nNota: Para respostas mais detalhadas, configure a chave GEMINI_API_KEY no ficheiro .env."

        if any(w in msg_lower for w in ['receita', 'revenue', 'negócio']):
            return f"Dados de receitas do observatório:\n\n{context}\n\nNota: Para análise com IA, configure a chave GEMINI_API_KEY."

        if any(w in msg_lower for w in ['quota', 'mercado', 'share']):
            return f"Dados de mercado:\n\n{context}\n\nNota: Para análise avançada, configure a chave GEMINI_API_KEY."

        return (
            f"Obrigado pela sua pergunta. Aqui está o contexto actual do mercado:\n\n{context}\n\n"
            "Para respostas mais inteligentes e análise em linguagem natural, "
            "configure a variável GEMINI_API_KEY no ficheiro .env com uma chave "
            "do Google AI Studio (gratuita em aistudio.google.com)."
        )
