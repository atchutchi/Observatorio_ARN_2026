"""
Comando para configurar tabelas e permissões no Supabase.
"""
from django.core.management.base import BaseCommand
from questionarios.utils import get_supabase_client
import time
import logging

logger = logging.getLogger(__name__)

# Lista de tabelas que precisam ser criadas no Supabase
TABLES_CONFIG = [
    {
        'name': 'tarifario_voz_orange_indicador',
        'description': 'Tarifário Orange (sincronizado do Django)',
    },
    {
        'name': 'tarifario_voz_telecel_indicador',
        'description': 'Tarifário TELECEL (sincronizado do Django)',
    },
    {
        'name': 'estacoes_moveis_indicador',
        'description': 'Estações Móveis (sincronizado do Django)',
    },
    {
        'name': 'trafego_originado_indicador',
        'description': 'Tráfego Originado (sincronizado do Django)',
    },
    {
        'name': 'trafego_terminado_indicador',
        'description': 'Tráfego Terminado (sincronizado do Django)',
    },
    {
        'name': 'trafego_roaming_internacional_indicador',
        'description': 'Tráfego Roaming Internacional (sincronizado do Django)',
    },
    {
        'name': 'lbi_indicador',
        'description': 'LBI (sincronizado do Django)',
    },
    {
        'name': 'trafego_internet_indicador',
        'description': 'Tráfego Internet (sincronizado do Django)',
    },
    {
        'name': 'internet_fixo_indicador',
        'description': 'Internet Fixo (sincronizado do Django)',
    },
    {
        'name': 'receitas_indicador',
        'description': 'Receitas (sincronizado do Django)',
    },
    {
        'name': 'emprego_indicador',
        'description': 'Emprego (sincronizado do Django)',
    },
    {
        'name': 'investimento_indicador',
        'description': 'Investimento (sincronizado do Django)',
    },
]

class Command(BaseCommand):
    help = 'Configura o Supabase criando tabelas necessárias para integração'

    def handle(self, *args, **options):
        """
        Execute o comando para configurar o Supabase.
        """
        self.stdout.write(self.style.MIGRATE_HEADING('Configurando tabelas no Supabase...'))
        
        try:
            # Tenta conectar ao Supabase
            supabase = get_supabase_client()
            
            # Para cada tabela na configuração
            for table_config in TABLES_CONFIG:
                table_name = table_config['name']
                
                # Verifica se a tabela existe (esta verificação é simulada)
                try:
                    # Tenta fazer uma consulta na tabela para ver se existe
                    self.stdout.write(f"Verificando tabela '{table_name}'...")
                    response = supabase.table(table_name).select("*").limit(1).execute()
                    self.stdout.write(self.style.SUCCESS(f"Tabela '{table_name}' já existe."))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"Atenção: A tabela '{table_name}' não pôde ser verificada. "
                        f"Erro: {str(e)}"
                    ))
                    self.stdout.write(
                        f"\nPara criar esta tabela manualmente no Supabase, siga estes passos:\n"
                        f"1. Acesse o Dashboard do Supabase\n"
                        f"2. Vá para 'Table Editor' > 'Create new table'\n"
                        f"3. Nome da tabela: {table_name}\n"
                        f"4. Descrição: {table_config['description']}\n"
                        f"5. Adicione as colunas necessárias (pelo menos 'django_id' como INTEGER)\n"
                        f"6. Adicione as colunas relevantes do modelo Django correspondente\n"
                    )
            
            self.stdout.write(self.style.SUCCESS('Verificação de tabelas concluída!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao configurar Supabase: {str(e)}'))
            self.stdout.write(self.style.WARNING(
                'ATENÇÃO: Para usar o Supabase corretamente, você precisa:\n'
                '1. Ter uma conta no Supabase (https://supabase.com)\n'
                '2. Configurar as credenciais no arquivo .env do projeto\n'
                '3. Criar manualmente as tabelas necessárias no painel do Supabase\n'
                '4. Garantir que cada tabela tenha um campo "django_id" para sincronização\n'
            ))
            return 