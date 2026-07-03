"""
Integração com APIs de IA Externa
HuggingFace + DeepSeek API
"""
import os
import requests
import json
from django.conf import settings

class HuggingFaceService:
    """Serviço de integração com HuggingFace"""
    
    def __init__(self):
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Modelos configurados
        self.models = {
            'conversational': 'microsoft/DialoGPT-medium',
            'classification': 'neuralmind/bert-base-portuguese-cased',
            'ner': 'pierreguillou/bert-base-cased-pt-ner',
            'sentiment': 'cardiffnlp/twitter-xlm-roberta-base-sentiment'
        }
    
    def classify_intent(self, text, candidate_labels):
        """Classifica intenção usando zero-shot classification"""
        if not self.api_token:
            return self._fallback_classification(text, candidate_labels)
        
        model_url = f"{self.base_url}/facebook/bart-large-mnli"
        
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": candidate_labels
            }
        }
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'labels' in result and 'scores' in result:
                    best_label = result['labels'][0]
                    confidence = result['scores'][0]
                    
                    return {
                        'intent': best_label,
                        'confidence': confidence,
                        'all_scores': dict(zip(result['labels'], result['scores']))
                    }
            
            return self._fallback_classification(text, candidate_labels)
            
        except Exception as e:
            print(f"Erro HuggingFace classification: {e}")
            return self._fallback_classification(text, candidate_labels)
    
    def extract_entities(self, text):
        """Extrai entidades nomeadas do texto"""
        if not self.api_token:
            return self._fallback_ner(text)
        
        model_url = f"{self.base_url}/{self.models['ner']}"
        
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"inputs": text}
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                entities = []
                for entity in result:
                    if entity.get('entity_group'):
                        entities.append({
                            'text': entity['word'],
                            'label': entity['entity_group'],
                            'confidence': entity['score'],
                            'start': entity['start'],
                            'end': entity['end']
                        })
                
                return entities
            
            return self._fallback_ner(text)
            
        except Exception as e:
            print(f"Erro HuggingFace NER: {e}")
            return self._fallback_ner(text)
    
    def generate_response(self, text, max_length=150):
        """Gera resposta conversacional"""
        if not self.api_token:
            return self._fallback_response(text)
        
        model_url = f"{self.base_url}/{self.models['conversational']}"
        
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": {
                "past_user_inputs": [],
                "generated_responses": [],
                "text": text
            },
            "parameters": {
                "max_length": max_length,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'generated_text' in result:
                    return result['generated_text']
                elif isinstance(result, dict) and 'bot' in result:
                    return result['bot']
                
            return self._fallback_response(text)
            
        except Exception as e:
            print(f"Erro HuggingFace generation: {e}")
            return self._fallback_response(text)
    
    def _fallback_classification(self, text, candidate_labels):
        """Classificação de fallback baseada em palavras-chave"""
        text_lower = text.lower()
        
        # Mapeamento simples de palavras-chave para intenções
        keyword_mapping = {
            'assinantes': ['assinantes', 'clientes', 'utilizadores', 'estações'],
            'trafego': ['tráfego', 'chamadas', 'minutos', 'voz'],
            'receitas': ['receitas', 'faturamento', 'fcfa', 'dinheiro'],
            'market_share': ['quota', 'market', 'share', 'percentagem'],
            'comparacao': ['comparar', 'versus', 'vs', 'diferença']
        }
        
        scores = {}
        for intent, keywords in keyword_mapping.items():
            if intent in candidate_labels:
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    scores[intent] = score / len(keywords)
        
        if scores:
            best_intent = max(scores, key=scores.get)
            return {
                'intent': best_intent,
                'confidence': scores[best_intent],
                'all_scores': scores
            }
        
        return {
            'intent': candidate_labels[0] if candidate_labels else 'unknown',
            'confidence': 0.1,
            'all_scores': {}
        }
    
    def _fallback_ner(self, text):
        """NER de fallback usando regex simples"""
        import re
        
        entities = []
        
        # Detectar anos
        years = re.findall(r'\b(20\d{2})\b', text)
        for year in years:
            entities.append({
                'text': year,
                'label': 'YEAR',
                'confidence': 0.9
            })
        
        # Detectar operadoras
        operators = ['TELECEL', 'Orange', 'TELECEL']
        for operator in operators:
            if operator.lower() in text.lower():
                entities.append({
                    'text': operator,
                    'label': 'OPERATOR',
                    'confidence': 0.95
                })
        
        return entities
    
    def _fallback_response(self, text):
        """Resposta de fallback simples"""
        responses = [
            "Entendi sua pergunta sobre dados de telecomunicações. Deixe-me consultar as informações.",
            "Vou buscar esses dados para você no sistema ARN.",
            "Processando sua consulta sobre o mercado de telecomunicações..."
        ]
        
        # Selecionar resposta baseada no hash do texto
        import hashlib
        text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return responses[text_hash % len(responses)]

class DeepSeekService:
    """Serviço de integração com DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com"
        
    def generate_response(self, messages, model="deepseek-chat"):
        """Gera resposta usando DeepSeek API"""
        if not self.api_key:
            return self._fallback_response()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            
            return self._fallback_response()
            
        except Exception as e:
            print(f"Erro DeepSeek API: {e}")
            return self._fallback_response()
    
    def analyze_with_reasoning(self, query, data_context):
        """Usa DeepSeek-R1 para análise avançada com raciocínio"""
        if not self.api_key:
            return self._fallback_analysis(query, data_context)
        
        system_prompt = """Você é um assistente especializado em análise de dados de telecomunicações da Guiné-Bissau. 
        Você tem acesso aos dados do mercado e deve fornecer análises precisas e insights baseados nos dados fornecidos.
        
        Sempre:
        - Use dados específicos quando disponíveis
        - Forneça contexto sobre o mercado da Guiné-Bissau
        - Mantenha respostas concisas mas informativas
        - Use formatação clara com números e percentuais
        """
        
        user_prompt = f"""
        Pergunta: {query}
        
        Dados disponíveis: {json.dumps(data_context, indent=2)}
        
        Por favor, analise os dados e forneça uma resposta detalhada.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_response(messages, model="deepseek-reasoner")
    
    def _fallback_response(self):
        """Resposta de fallback quando API não está disponível"""
        return "Desculpe, estou com dificuldades técnicas no momento. Tente novamente em alguns instantes."
    
    def _fallback_analysis(self, query, data_context):
        """Análise de fallback simples"""
        return f"Consultei os dados sobre '{query}'. Os resultados estão disponíveis no contexto fornecido."

class AIOrchestrator:
    """Orquestrador que combina múltiplos serviços de IA"""
    
    def __init__(self):
        self.huggingface = HuggingFaceService()
        self.deepseek = DeepSeekService()
        
    def process_query(self, text, data_context=None):
        """Processa query usando múltiplos serviços de IA"""
        
        # 1. Classificar intenção com HuggingFace
        candidate_labels = [
            'consulta_assinantes', 'analise_trafego', 'market_share',
            'receitas', 'comparacao_operadores', 'tendencias',
            'investimentos', 'saudacao', 'despedida'
        ]
        
        intent_result = self.huggingface.classify_intent(text, candidate_labels)
        
        # 2. Extrair entidades
        entities = self.huggingface.extract_entities(text)
        
        # 3. Se há contexto de dados, usar DeepSeek para análise avançada
        if data_context and intent_result['confidence'] > 0.6:
            advanced_response = self.deepseek.analyze_with_reasoning(text, data_context)
            
            return {
                'response': advanced_response,
                'intent': intent_result['intent'],
                'confidence': intent_result['confidence'],
                'entities': entities,
                'source': 'deepseek_analysis'
            }
        
        # 4. Fallback para resposta simples
        simple_response = self.huggingface.generate_response(text)
        
        return {
            'response': simple_response,
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'entities': entities,
            'source': 'huggingface_simple'
        }
    
    def enhance_response_with_data(self, base_response, data):
        """Melhora resposta base com dados específicos"""
        
        if not data or data.get('erro'):
            return base_response
        
        # Adicionar estatísticas relevantes
        enhanced = base_response
        
        if data.get('tipo') == 'assinantes':
            total = data.get('totais', {}).get('total_assinantes', 0)
            enhanced += f"\n\n📊 Dados atuais: {total:,} assinantes no total"
            
        elif data.get('tipo') == 'receitas':
            total = data.get('totais', {}).get('total_receitas', 0)
            enhanced += f"\n\n💰 Receitas: {total/1000000:,.0f} milhões FCFA"
            
        elif data.get('tipo') == 'market_share' and data.get('lider'):
            lider = data['lider']
            enhanced += f"\n\n🏆 Líder: {lider['operadora']} com {lider['percentual']}%"
        
        return enhanced
    
    def generate_suggestions(self, intent, entities):
        """Gera sugestões baseadas na intenção e entidades"""
        
        base_suggestions = {
            'consulta_assinantes': [
                "Mostre o crescimento de assinantes",
                "Compare assinantes entre operadoras",
                "Qual a taxa de penetração?",
                "Evolução por trimestre"
            ],
            'market_share': [
                "Compare market share histórico",
                "Qual operadora cresceu mais?",
                "Análise de competitividade",
                "Projeção de market share"
            ],
            'receitas': [
                "Análise de rentabilidade",
                "Crescimento de receitas",
                "Compare receitas por serviço",
                "ROI por operadora"
            ],
            'analise_trafego': [
                "Padrões de uso de tráfego",
                "Picos de tráfego",
                "Eficiência de rede",
                "Tráfego internacional"
            ]
        }
        
        suggestions = base_suggestions.get(intent, [
            "Mostre dados de assinantes",
            "Análise de market share",
            "Compare operadoras",
            "Tendências do mercado"
        ])
        
        # Personalizar sugestões baseado nas entidades
        if 'operadora' in entities:
            operadora = entities['operadora']
            suggestions = [s.replace('operadoras', operadora).replace('Compare', f'Analise {operadora}') for s in suggestions]
        
        if 'ano' in entities:
            ano = entities['ano']
            suggestions = [f"{s} em {ano}" for s in suggestions]
        
        return suggestions[:4]  # Máximo 4 sugestões
