"""
Utilities for the questionarios app, including Supabase integration.
"""
import os
from django.conf import settings
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Retorna um cliente para interagir com o Supabase.
    
    Returns:
        Client: O cliente Supabase configurado com as credenciais do .env
    """
    try:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_KEY
        
        if not url or not key:
            raise ValueError("As credenciais do Supabase não estão configuradas corretamente")
        
        supabase = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"Erro ao conectar com Supabase: {str(e)}")
        # Fallback para o mock apenas em caso de erro
        return _get_mock_client()

def _get_mock_client():
    """
    Retorna um cliente mock para desenvolvimento quando o Supabase não está disponível.
    Apenas para uso em desenvolvimento.
    """
    class SupabaseMock:
        def table(self, table_name):
            print(f"[Mock] Acessando tabela: {table_name}")
            return self
            
        def upsert(self, data):
            print(f"[Mock] Inserindo/atualizando dados: {data}")
            return self
            
        def delete(self):
            print("[Mock] Excluindo registros")
            return self
            
        def eq(self, field, value):
            print(f"[Mock] Condição eq({field}, {value})")
            return self
            
        def execute(self):
            print("[Mock] Executando operação")
            return {"data": []}
    
    print("ATENÇÃO: Usando cliente Supabase MOCK. Os dados NÃO serão persistidos no Supabase.")
    return SupabaseMock() 