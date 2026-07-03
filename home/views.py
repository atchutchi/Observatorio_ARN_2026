from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Max, F, DecimalField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.core.cache import cache
from decimal import Decimal

from .models import Operadora, DadoEstatistico, TipoServico, Notification, UserActivity
from .chatbot import Chatbot
from questionarios.models import (
    AssinantesIndicador, ReceitasIndicador, InvestimentoIndicador
)
import logging

logger = logging.getLogger(__name__)

# Initialize chatbot instance (can be global if state is managed via session)
chatbot_instance = Chatbot()

# Helper function to get latest year with data for a model
def get_latest_year(model):
    return model.objects.aggregate(latest_year=Max('ano')).get('latest_year')

def _get_home_market_context():
    """Carrega e guarda em cache os números pesados da tela inicial.

    O login redireciona para ``/``; sem cache, cada entrada executava várias
    agregações de KPIs antes de renderizar o dashboard, dando a sensação de
    que o login estava lento. O cache é curto para manter os dados recentes e
    remover esse custo do caminho crítico de autenticação.
    """

    cache_key = 'home_market_context_v1'
    cached_context = cache.get(cache_key)
    if cached_context is not None:
        return cached_context

    market_context = {
        'total_assinantes': 0,
        'total_receitas': Decimal('0'),
        'total_investimento': Decimal('0'),
        'num_operadoras': 0,
    }

    try:
        latest_year = get_latest_year(AssinantesIndicador)
        if latest_year:
            assinantes_data = AssinantesIndicador.objects.filter(ano=latest_year)
            assinantes_expr = F('assinantes_pre_pago') + F('assinantes_pos_pago')
            market_context['total_assinantes'] = assinantes_data.aggregate(
                total=Sum(assinantes_expr)
            )['total'] or 0
            market_context['assinantes_por_operadora'] = [
                {
                    'operadora': item['operadora'],
                    'assinantes': item['total_assinantes'],
                }
                for item in assinantes_data.values('operadora').annotate(
                    total_assinantes=Sum(assinantes_expr)
                )
            ]
            market_context['latest_year'] = latest_year
            market_context['num_operadoras'] = assinantes_data.values('operadora').distinct().count()

        latest_year_receitas = get_latest_year(ReceitasIndicador)
        if latest_year_receitas:
            market_context['total_receitas'] = ReceitasIndicador.objects.filter(
                ano=latest_year_receitas
            ).aggregate(total=Sum('receita_total'))['total'] or Decimal('0')

        latest_year_invest = get_latest_year(InvestimentoIndicador)
        if latest_year_invest:
            market_context['total_investimento'] = InvestimentoIndicador.objects.filter(
                ano=latest_year_invest
            ).aggregate(total=Sum('investimento_total'))['total'] or Decimal('0')
    except Exception as e:
        logger.error(f"Erro ao carregar dados da home: {e}")

    cache.set(cache_key, market_context, 60 * 5)
    return market_context


def index(request):
    """View principal da home page com estatísticas do mercado."""
    context = {
        'title': 'Observatório do Mercado de Telecomunicações',
        'page': 'home',
        **_get_home_market_context(),
    }

    # Usar template diferente se usuário estiver autenticado
    template = 'home/dashboard.html' if request.user.is_authenticated else 'home/index.html'
    return render(request, template, context)

@login_required
def profile(request):
    """View para a página de perfil do usuário."""
    context = {
        'title': 'Perfil',
        'page': 'profile'
    }
    return render(request, 'account/profile.html', context)

def dashboard(request):
    """View para o dashboard principal."""
    context = {
        'title': 'Dashboard',
        'page': 'dashboard'
    }
    return render(request, 'home/dashboard.html', context)

def estatisticas(request):
    """View para a página de estatísticas."""
    context = {
        'title': 'Estatísticas',
        'page': 'estatisticas'
    }
    return render(request, 'home/estatisticas.html', context)

def operadoras(request):
    """View para a página de operadoras."""
    context = {
        'title': 'Operadoras',
        'page': 'operadoras'
    }
    return render(request, 'home/operadoras.html', context)

def relatorios(request):
    """View para a página de relatórios."""
    context = {
        'title': 'Relatórios',
        'page': 'relatorios'
    }
    return render(request, 'home/relatorios.html', context)

def sobre(request):
    """View para a página sobre."""
    context = {
        'title': 'Sobre',
        'page': 'sobre'
    }
    return render(request, 'home/sobre.html', context)

def chatbot_page_view(request):
    """View para a página do chatbot - renderiza a página de chatbot com contexto adequado."""
    context = {
        'title': 'Chatbot ARN',
        'page': 'chatbot'
    }
    return render(request, 'home/chatbot.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotAPIView(View):
    """API endpoint para interações com o chatbot."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({
                    'error': 'Mensagem vazia'
                }, status=400)
            
            # Process message through chatbot
            bot_response = chatbot_instance.get_response(user_message)
            
            return JsonResponse({
                'response': bot_response,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            logger.error(f"Erro no chatbot: {e}")
            return JsonResponse({
                'error': 'Erro interno do servidor'
            }, status=500)
    
    def get(self, request):
        return JsonResponse({
            'error': 'Método não permitido'
        }, status=405)

def chatbot(request):
    """View para a página do chatbot."""
    context = {
        'title': 'Chatbot',
        'page': 'chatbot'
    }
    return render(request, 'home/chatbot.html', context)

@login_required
def notifications_api(request):
    """API para buscar notificações do usuário"""
    if request.method == 'GET':
        notifications = Notification.objects.filter(user=request.user)[:10]
        data = []
        for notification in notifications:
            data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'notifications': data,
            'unread_count': unread_count
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
def mark_notification_read(request, notification_id):
    """API para marcar notificação como lida"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notificação não encontrada'}, status=404)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
def mark_all_notifications_read(request):
    """API para marcar todas as notificações como lidas"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def create_welcome_notification(user):
    """Criar notificação de boas-vindas para novos usuários"""
    Notification.create_notification(
        user=user,
        title="Bem-vindo à ARN Platform!",
        message="Explore os dados e análises do mercado de telecomunicações da Guiné-Bissau.",
        notification_type='success'
    ) 