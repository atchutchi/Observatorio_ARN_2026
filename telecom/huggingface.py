import os
import json
import requests
from django.conf import settings

def get_inference_api(model_name):
    """
    Retorna uma função que faz chamadas à API de inferência do Hugging Face.
    
    Args:
        model_name (str): Nome do modelo no Hugging Face Hub
        
    Returns:
        function: Função que recebe uma entrada e retorna a saída do modelo
    """
    # Verificar se temos o token da API
    api_token = getattr(settings, 'HUGGINGFACE_TOKEN', None)
    
    # Função que será retornada e usada para fazer chamadas à API
    def inference_function(inputs):
        # Modo offline - retorna respostas padrão
        if not api_token or os.environ.get("OFFLINE_MODE", "False").lower() == "true":
            return [{"generated_text": get_fallback_response(inputs)}]
        
        # URL da API
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        # Cabeçalhos HTTP com o token de autenticação
        headers = {"Authorization": f"Bearer {api_token}"}
        
        try:
            # Chamada à API
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": inputs}
            )
            
            # Verificar se a resposta foi bem-sucedida
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro na API do Hugging Face: Status {response.status_code}")
                print(f"Resposta: {response.text}")
                return [{"generated_text": get_fallback_response(inputs)}]
                
        except Exception as e:
            print(f"Erro ao chamar API do Hugging Face: {e}")
            return [{"generated_text": get_fallback_response(inputs)}]
    
    return inference_function

def get_fallback_response(inputs):
    """
    Gera uma resposta padrão quando a API não está disponível.
    
    Args:
        inputs (str): A pergunta ou prompt
        
    Returns:
        str: Uma resposta padrão
    """
    # Extrair a pergunta do prompt (que pode ser um prompt elaborado)
    if "Pergunta:" in inputs:
        question = inputs.split("Pergunta:")[1].split("\n")[0].strip()
    else:
        question = inputs
    
    question_lower = question.lower()
    
    # Respostas padrão baseadas em palavras-chave
    if any(word in question_lower for word in ["operadora", "empresa", "orange", "telecel", "telecel"]):
        return "O mercado de telecomunicações da Guiné-Bissau é composto principalmente por duas operadoras: Orange e TELECEL. Cada uma possui diferentes níveis de penetração no mercado."
    
    elif any(word in question_lower for word in ["assinante", "usuário", "cliente", "subscritores"]):
        return "Os dados de assinantes variam por operadora e são atualizados periodicamente através dos questionários. Para dados específicos, verifique os relatórios disponíveis."
    
    elif any(word in question_lower for word in ["receita", "faturamento", "rendimento"]):
        return "As receitas das operadoras são divididas em grossistas e retalhistas. O sistema coleta esses dados através de questionários periódicos."
    
    elif any(word in question_lower for word in ["tráfego", "chamada", "minuto", "comunicação"]):
        return "O tráfego de comunicações é medido em chamadas on-net (dentro da mesma operadora) e off-net (entre operadoras diferentes). Esses dados são coletados regularmente para análise."
    
    elif any(word in question_lower for word in ["questionário", "formulário", "pesquisa"]):
        return "Os questionários são ferramentas essenciais para a coleta de dados atualizados do mercado de telecomunicações. Eles são aplicados periodicamente às operadoras."
    
    else:
        return "Não tenho informações específicas sobre essa pergunta. Posso ajudar com dados sobre operadoras, assinantes, receitas, tráfego e outros indicadores do mercado de telecomunicações da Guiné-Bissau." 