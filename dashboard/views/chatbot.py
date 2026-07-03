# dashboard/views/chatbot.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
import time

from dashboard.models import ChatSession, ChatMessage
from ..services.ai_service import ARNAssistantService
from ..services.ai_integration import AIOrchestrator

@login_required
def chatbot_arn_view(request):
    """
    View principal do novo Assistente ARN Analytics
    """
    context = {
        'title': 'Assistente ARN Analytics',
        'page': 'chatbot_arn'
    }
    return render(request, 'dashboard/chatbot/arn_assistant.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class ARNChatbotAPIView(View):
    """API principal do Assistente ARN Analytics"""
    
    def __init__(self):
        super().__init__()
        self.assistant_service = ARNAssistantService()
        self.ai_orchestrator = AIOrchestrator()
    
    def post(self, request):
        """Processa mensagens do chat"""
        try:
            data = json.loads(request.body)
            mensagem = data.get('message', '').strip()
            sessao_id = data.get('session_id')
            
            if not mensagem:
                return JsonResponse({
                    'error': 'Mensagem vazia'
                }, status=400)
            
            # Processar mensagem usando o serviço ARN
            start_time = time.time()
            resultado = self.assistant_service.processar_mensagem(
                mensagem=mensagem,
                usuario=request.user,
                sessao_id=sessao_id
            )
            
            # Se temos dados estruturados, usar AI avançada para melhorar resposta
            if resultado.get('dados') and resultado['confianca'] > 0.6:
                try:
                    ai_result = self.ai_orchestrator.process_query(
                        mensagem, 
                        resultado['dados']
                    )
                    
                    # Combinar resultados
                    if ai_result.get('response') and len(ai_result['response']) > 50:
                        resultado['resposta'] = ai_result['response']
                        resultado['ai_enhanced'] = True
                        resultado['ai_source'] = ai_result.get('source', 'unknown')
                    
                except Exception as e:
                    print(f"Erro AI enhancement: {e}")
                    # Continuar com resposta padrão
            
            processing_time = time.time() - start_time
            
            return JsonResponse({
                'response': resultado['resposta'],
                'data': resultado.get('dados'),
                'charts': resultado.get('graficos', []),
                'suggestions': resultado.get('sugestoes', []),
                'intent': resultado.get('intencao'),
                'confidence': resultado.get('confianca'),
                'session_id': resultado.get('sessao_id'),
                'processing_time': round(processing_time, 3),
                'ai_enhanced': resultado.get('ai_enhanced', False),
                'timestamp': timezone.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Erro interno: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """Retorna informações da sessão atual"""
        try:
            sessao_id = request.GET.get('session_id')
            
            if sessao_id:
                # Buscar histórico da sessão
                historico = self.assistant_service.obter_historico_sessao(sessao_id)
                
                return JsonResponse({
                    'session_id': sessao_id,
                    'history': historico,
                    'status': 'active'
                })
            else:
                # Criar nova sessão
                nova_sessao = self.assistant_service.criar_nova_sessao(request.user)
                
                return JsonResponse({
                    'session_id': str(nova_sessao.id),
                    'status': 'new_session',
                    'welcome_message': {
                        'text': "Olá! Sou o Assistente ARN Analytics. Posso ajudar você com dados sobre o mercado de telecomunicações da Guiné-Bissau.",
                        'suggestions': [
                            "Qual a quota de mercado da Orange?",
                            "Mostre os dados de assinantes de 2023",
                            "Compare TELECEL e Orange em receitas",
                            "Como evoluiu o tráfego nos últimos anos?"
                        ]
                    }
                })
                
        except Exception as e:
            return JsonResponse({
                'error': f'Erro ao obter sessão: {str(e)}'
            }, status=500)

@login_required
def chat_history_view(request):
    """View para histórico de conversas"""
    sessoes = ChatSession.objects.filter(usuario=request.user)[:10]
    
    context = {
        'title': 'Histórico de Conversas',
        'sessoes': sessoes
    }
    return render(request, 'dashboard/chatbot/chat_history.html', context)

@login_required
def chat_session_detail(request, session_id):
    """Detalhes de uma sessão específica"""
    try:
        sessao = ChatSession.objects.get(id=session_id, usuario=request.user)
        mensagens = sessao.mensagens.all()
        
        context = {
            'title': f'Conversa {session_id}',
            'sessao': sessao,
            'mensagens': mensagens
        }
        return render(request, 'dashboard/chatbot/session_detail.html', context)
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Sessão não encontrada'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ChatFeedbackAPIView(View):
    """API para feedback das respostas"""
    
    def post(self, request):
        """Salva feedback do usuário"""
        try:
            data = json.loads(request.body)
            message_id = data.get('message_id')
            rating = data.get('rating')
            comment = data.get('comment', '')
            
            if not message_id or not rating:
                return JsonResponse({
                    'error': 'message_id e rating são obrigatórios'
                }, status=400)
            
            # Buscar mensagem
            try:
                mensagem = ChatMessage.objects.get(
                    id=message_id,
                    sessao__usuario=request.user
                )
            except ChatMessage.DoesNotExist:
                return JsonResponse({
                    'error': 'Mensagem não encontrada'
                }, status=404)
            
            # Salvar feedback (implementar modelo de feedback se necessário)
            # Para agora, apenas retornar sucesso
            
            return JsonResponse({
                'success': True,
                'message': 'Feedback recebido com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Erro ao salvar feedback: {str(e)}'
            }, status=500)

# Manter views antigas para compatibilidade
def chatbot_view(request):
    """View do chatbot antigo (redirecionar para novo)"""
    return chatbot_arn_view(request)

@csrf_exempt  
def chatbot_api(request):
    """API do chatbot antigo (redirecionar para novo)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            
            if not question:
                return JsonResponse({'error': 'Pergunta vazia'}, status=400)
            
            # Usar novo serviço
            assistant = ARNAssistantService()
            resultado = assistant.processar_mensagem(
                mensagem=question,
                usuario=request.user
            )
            
            return JsonResponse({
                'response': resultado['resposta'],
                'timestamp': timezone.now().strftime('%H:%M')
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)