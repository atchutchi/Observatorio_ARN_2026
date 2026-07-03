import os
import json
import logging
import re
import uuid # Import uuid
from typing import Optional, Dict, List, Any
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Sum, Avg, Max # Import aggregators
from decimal import Decimal

# Import Hugging Face client
from huggingface_hub import InferenceClient

# Import your actual indicator models 
# (Ensure all necessary models are imported)
from questionarios.models import (
    EstacoesMoveisIndicador, TrafegoOriginadoIndicador, TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador, LBIIndicador, TrafegoInternetIndicador,
    InternetFixoIndicador, TarifarioVozOrangeIndicador, TarifarioVozMTNIndicador,
    ReceitasIndicador, EmpregoIndicador, InvestimentoIndicador, AssinantesIndicador,
    TarifarioVozTelecelIndicador # Add the new Telecel model
)
# Assuming Operadora choices are defined in a base model or settings
from questionarios.models.base import IndicadorBase 

# Configure logging
logger = logging.getLogger(__name__)

class Chatbot:
    """
    Classe para gerenciar a comunicação com a API da Hugging Face
    com foco no Observatório do Mercado de Telecomunicações da Guiné-Bissau.
    Adaptação do exemplo fornecido.
    """
    def __init__(self):
        self.api_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        self.model = getattr(settings, 'HUGGINGFACE_MODEL', "mistralai/Mistral-7B-Instruct-v0.2")
        self.max_tokens = getattr(settings, 'CHATBOT_MAX_TOKENS', 500) # Reduced for performance
        self.temperature = getattr(settings, 'CHATBOT_TEMPERATURE', 0.6)
        self.cache_prefix = "chatbot_session_"
        self.system_message = """
        Você é um assistente amigável e prestativo do Observatório do Mercado de Telecomunicações da Guiné-Bissau (ARN - Autoridade Reguladora Nacional).
        Seu objetivo é fornecer informações concisas e precisas sobre o mercado de telecomunicações da Guiné-Bissau com base nos dados disponíveis.
        
        Contexto Principal:
        - Operadoras Ativas: Orange, TELECEL, TELECEL.
        - Foco: Dados estatísticos mensais e trimestrais sobre assinantes, tráfego, receitas, investimento, emprego, tarifas.
        
        Instruções de Resposta:
        1. Responda sempre em Português de Portugal ou Guiné-Bissau.
        2. Seja cordial, profissional e direto ao ponto. Evite introduções longas.
        3. Se a informação exata for solicitada (ex: "Qual a receita da Orange em Janeiro de 2024?"), tente buscar no banco de dados primeiro.
        4. Se não encontrar no banco ou a pergunta for geral (ex: "Como está o mercado?"), use seu conhecimento geral e o contexto fornecido.
        5. Se não souber a resposta ou não tiver dados, admita educadamente e sugira consultar os relatórios ou a seção de estatísticas do site.
        6. Para perguntas sobre tarifas, mencione que os preços podem variar e sugira consultar os sites oficiais das operadoras ou os dados específicos de tarifas no observatório.
        7. Mantenha as respostas relativamente curtas e focadas na pergunta.
        8. Responda a saudações de forma breve e educada.
        """
        # Note: Initial history is now loaded/created per session in get_conversation_history
    
    def get_session_id(self, session_id: Optional[str] = None) -> str:
        """Obtém ou gera um ID de sessão único."""
        if not session_id or not isinstance(session_id, str) or not session_id.strip():
            session_id = str(uuid.uuid4())
        return session_id
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Recupera o histórico de conversa do cache ou cria um novo."""
        cache_key = f"{self.cache_prefix}{session_id}"
        history = cache.get(cache_key)
        
        if not history or not isinstance(history, list):
            logger.info(f"Iniciando novo histórico de conversa para session_id: {session_id}")
            history = [{"role": "system", "content": self.system_message}]
            # Salva o histórico inicial imediatamente
            self.save_conversation_history(session_id, history)
            
        # Ensure the history always starts with the system message
        if not history or history[0].get('role') != 'system':
             history = [{"role": "system", "content": self.system_message}] + (history or [])
             
        return history
    
    def save_conversation_history(self, session_id: str, history: List[Dict[str, str]]) -> None:
        """Salva o histórico de conversa no cache."""
        if not session_id or not history:
            return
        cache_key = f"{self.cache_prefix}{session_id}"
        # Limit history size to prevent excessive cache/prompt size (e.g., last 10 messages + system)
        max_history = 10 
        limited_history = [history[0]] + history[-(max_history*2):] # Keep system + last N user/assistant pairs
        cache.set(cache_key, limited_history, 60 * 30) # Salvar por 30 minutos
    
    def reset_conversation(self, session_id: str) -> None:
        """Reinicia o histórico da conversa para a sessão."""
        if session_id:
            cache_key = f"{self.cache_prefix}{session_id}"
            cache.delete(cache_key)
            logger.info(f"Histórico de conversa resetado para session_id: {session_id}")
    
    def get_response(self, user_message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Processa a mensagem do usuário e retorna uma resposta."""
        session_id = self.get_session_id(session_id)
        logger.info(f"Processando mensagem para session_id: {session_id}")
        
        try:
            if not user_message or not user_message.strip():
                return self._handle_error("Por favor, digite uma mensagem válida.", "empty_message", session_id)

            conversation_history = self.get_conversation_history(session_id)

            # Adiciona a mensagem atual do usuário ao histórico ANTES de qualquer processamento
            conversation_history.append({"role": "user", "content": user_message})

            # --- Tratamento de Casos Específicos (Saudações, Fallbacks Locais) --- 
            is_greeting, greeting_response = self._handle_greeting(user_message)
            if is_greeting:
                conversation_history.append({"role": "assistant", "content": greeting_response})
                self.save_conversation_history(session_id, conversation_history)
                return {"message": greeting_response, "session_id": session_id, "status": "success"}

            # --- Busca no Banco de Dados (Simplificada) --- 
            database_response = self._search_database_simple(user_message)
            if database_response:
                logger.info("Resposta encontrada no banco de dados.")
                conversation_history.append({"role": "assistant", "content": database_response})
                self.save_conversation_history(session_id, conversation_history)
                return {"message": database_response, "session_id": session_id, "status": "success", "source": "database"}
            
            # --- Fallback para Respostas Locais (se API falhar ou não configurada) --- 
            if not self.api_token:
                logger.warning("API key não configurada. Usando fallback local.")
                fallback_resp = self._get_local_fallback(user_message)
                conversation_history.append({"role": "assistant", "content": fallback_resp})
                self.save_conversation_history(session_id, conversation_history)
                return {"message": fallback_resp, "session_id": session_id, "status": "success", "using_fallback": True, "fallback_reason": "api_key_missing"}

            # --- Chamada à API Hugging Face --- 
            logger.info(f"Enviando para API Hugging Face. Histórico: {len(conversation_history)} mensagens.")
            try:
                client = InferenceClient(model=self.model, token=self.api_token)
                formatted_prompt = self._format_history_for_mistral(conversation_history)
                
                api_response_raw = client.text_generation(
                    formatted_prompt,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                )
                
                assistant_message = self._process_mistral_response(api_response_raw)
                logger.info(f"Resposta recebida da API (processada): {assistant_message[:100]}...")

                conversation_history.append({"role": "assistant", "content": assistant_message})
                self.save_conversation_history(session_id, conversation_history)
                
                return {"message": assistant_message, "session_id": session_id, "status": "success", "source": "model"}
                
            except Exception as api_error:
                logger.error(f"Erro na API Hugging Face: {str(api_error)}", exc_info=True)
                fallback_resp = self._get_local_fallback(user_message)
                conversation_history.append({"role": "assistant", "content": fallback_resp}) # Log fallback answer
                self.save_conversation_history(session_id, conversation_history) # Save history even on API error
                return {"message": fallback_resp, "session_id": session_id, "status": "success", "using_fallback": True, "fallback_reason": "api_error"}

        except Exception as e:
            logger.error(f"Erro geral em get_response: {str(e)}", exc_info=True)
            return self._handle_error("Ocorreu um erro inesperado. Tente novamente.", "general_error", session_id)
    
    def _handle_greeting(self, user_message: str) -> (bool, Optional[str]):
        """Verifica e retorna uma resposta para saudações simples."""
        saudacoes = ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "boas", "hey", "hi", "hello"]
        msg_lower = user_message.lower().strip()
        is_greeting = msg_lower in saudacoes or any(msg_lower.startswith(s + " ") for s in saudacoes)
        
        if is_greeting:
            import random
            greeting_responses = [
                "Olá! Como posso ajudar com informações sobre o mercado de telecomunicações da Guiné-Bissau?",
                "Oi! Em que posso ser útil hoje sobre as telecomunicações em GB?",
                "Boas! Precisa de alguma informação específica do Observatório?"
            ]
            return True, random.choice(greeting_responses)
        return False, None
        
    def _search_database_simple(self, query: str) -> Optional[str]:
        """Realiza uma busca MUITO SIMPLIFICADA no banco de dados por palavras-chave."""
        query_lower = query.lower()
        latest_year = AssinantesIndicador.objects.aggregate(Max('ano')).get('ano__max')
        
        if not latest_year:
             return None # No data to search

        response = None
        
        # Exemplo: Buscar total de assinantes
        if "assinantes" in query_lower or "subscritores" in query_lower:
            total = AssinantesIndicador.objects.filter(ano=latest_year).aggregate(
                total_pre=Sum('assinantes_pre_pago'),
                total_pos=Sum('assinantes_pos_pago'),
                total_fixo=Sum('assinantes_fixo')
            )
            total_geral = (total.get('total_pre') or 0) + (total.get('total_pos') or 0) + (total.get('total_fixo') or 0)
            if total_geral > 0:
                response = f"Em {latest_year}, o número total de assinantes (pré+pós+fixo) reportado foi de aproximadamente {total_geral:,.0f}." 

        # Exemplo: Buscar receita total
        elif "receita" in query_lower or "faturamento" in query_lower:
             total_receita = ReceitasIndicador.objects.filter(ano=latest_year).aggregate(total=Sum('receitas_total_calculado')) # Assuming calculated field
             if total_receita and total_receita.get('total'):
                 response = f"A receita total do setor reportada em {latest_year} foi de aproximadamente {total_receita['total']:,.0f} XOF." 

        # Exemplo: Buscar investimento total
        elif "investimento" in query_lower:
            total_inv = InvestimentoIndicador.objects.filter(ano=latest_year).aggregate(
                corp=Sum('total_corporeo'), # Assuming calculated field
                incorp=Sum('total_incorporeo') # Assuming calculated field
            )
            total_geral = (total_inv.get('corp') or 0) + (total_inv.get('incorp') or 0)
            if total_geral > 0:
                response = f"O investimento total (corpóreo + incorpóreo) reportado em {latest_year} foi de aproximadamente {total_geral:,.0f} XOF."

        if response:
            return response + " (Fonte: Dados do Observatório)"
            
        return None # Se nenhuma palavra-chave corresponder

    def _get_local_fallback(self, user_message: str) -> str:
        """Gera uma resposta local genérica ou baseada em palavras-chave simples."""
        query_lower = user_message.lower()
        
        if "operadoras" in query_lower:
            return "As principais operadoras na Guiné-Bissau são Orange, TELECEL e TELECEL."
        elif "relatório" in query_lower:
            return "Você pode encontrar relatórios detalhados na seção 'Relatórios' do site."
        elif "estatísticas" in query_lower:
            return "A seção 'Estatísticas' contém diversos dados sobre o mercado. Qual indicador específico você procura?"
        else:
            return "Desculpe, não consegui buscar a informação no momento. Por favor, tente reformular ou consulte as seções do site."

    def _format_history_for_mistral(self, history: List[Dict[str, str]]) -> str:
        """Formata histórico para Mistral Instruct."""
        prompt = ""
        # Add system prompt first if it exists and seems correct
        if history and history[0]["role"] == "system":
            prompt += f"<s>[INST] {history[0]['content']} [/INST]</s>\n"
            current_history = history[1:]
        else:
             # Fallback if system prompt is missing or history is malformed
             prompt += f"<s>[INST] {self.system_message} [/INST]</s>\n"
             current_history = history

        # Add user/assistant turns
        for i in range(0, len(current_history), 2):
            user_turn = current_history[i]
            if user_turn["role"] == "user":
                 prompt += f"<s>[INST] {user_turn['content']} [/INST]"
                 if i + 1 < len(current_history):
                    assistant_turn = current_history[i+1]
                    if assistant_turn["role"] == "assistant":
                        prompt += f" {assistant_turn['content']}</s>\n"
                    else: # Handle case where roles are incorrect
                        prompt += "</s>\n" 
                 else: # Last user message
                     prompt += ""
            else: # Handle case where roles start incorrectly
                 prompt += f" {user_turn['content']}</s>\n" 

        return prompt

    def _process_mistral_response(self, response) -> str:
        """Limpa a resposta bruta do modelo Mistral."""
        # A InferenceApi retorna uma lista de dicionários ou um dicionário
        if isinstance(response, list) and len(response) > 0:
            # Pega o primeiro resultado
            text = response[0].get('generated_text', '')
        elif isinstance(response, dict):
            text = response.get('generated_text', '')
        else:
            text = str(response)
        
        # Remove tags and potential artifacts
        cleaned = text.replace("<s>", "").replace("</s>", "")
        
        # Mistral often repeats the last instruction/user message.
        # We try to remove this if the response starts with '[INST]' or the last user message.
        # This part needs access to the *last* user message which isn't directly passed here.
        # A simpler approach: just strip leading/trailing whitespace.
        return cleaned.strip()

    def _handle_error(self, message: str, error_type: str, session_id: str) -> Dict[str, Any]:
        """Formata a resposta de erro."""
        logger.error(f"Erro {error_type} para session_id {session_id}: {message}")
        return {
            "message": message,
            "session_id": session_id,
            "status": "error",
            "error_type": error_type
        } 