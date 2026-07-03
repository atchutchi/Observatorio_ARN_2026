import logging
from django.core.management.base import BaseCommand
from django.db import connection
from observatorio.utils.db_utils import (
    check_table_exists, 
    check_column_exists, 
    log_missing_tables_and_columns
)

logger = logging.getLogger('observatorio.migrations')

class Command(BaseCommand):
    help = 'Verifica a integridade do banco de dados e registra problemas encontrados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Exibe informações detalhadas sobre todas as tabelas e colunas',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Tenta corrigir automaticamente problemas encontrados (quando possível)',
        )

    def handle(self, *args, **options):
        """Executa a verificação da integridade do banco de dados."""
        self.stdout.write('Iniciando verificação da integridade do banco de dados...')
        
        # Verifica tabelas e colunas faltantes
        log_missing_tables_and_columns()
        
        # Verifica tabelas problemáticas específicas
        problem_tables = self.check_known_problem_tables()
        
        if problem_tables:
            self.stdout.write(
                self.style.WARNING(f'Foram encontrados problemas em {len(problem_tables)} tabelas:')
            )
            for table in problem_tables:
                self.stdout.write(f"  - {table}")
                
            if options['fix']:
                self.stdout.write('Tentando corrigir problemas automaticamente...')
                from django.core.management import call_command
                try:
                    call_command('fix_database', backup=True)
                    self.stdout.write(self.style.SUCCESS('Correções aplicadas com sucesso!'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao aplicar correções: {str(e)}'))
        else:
            self.stdout.write(
                self.style.SUCCESS('Nenhum problema conhecido foi encontrado no banco de dados.')
            )
            
        if options['detailed']:
            self.print_database_schema()
        
        self.stdout.write(self.style.SUCCESS('Verificação do banco de dados concluída.'))

    def check_known_problem_tables(self):
        """Verifica tabelas específicas que sabemos que podem ter problemas."""
        problem_tables = []
        
        # Lista de tabelas e colunas a verificar
        tables_to_check = {
            'questionarios_trafegooriginadoindicador': [],
            'questionarios_estacoesmoveisindicador': [
                'total_carregamentos', 
                'total_carregamentos_mulher', 
                'total_carregamentos_homem'
            ],
            'questionarios_investimentoindicador': []
        }
        
        for table_name, columns in tables_to_check.items():
            # Verifica se a tabela existe
            if not check_table_exists(table_name):
                problem_tables.append(f"{table_name} (tabela ausente)")
                logger.error(f"Tabela ausente: {table_name}")
                continue
            
            # Verifica colunas específicas, se houver
            if columns:
                missing_columns = []
                for column in columns:
                    if not check_column_exists(table_name, column):
                        missing_columns.append(column)
                        logger.error(f"Coluna ausente: {column} na tabela {table_name}")
                
                if missing_columns:
                    problem_tables.append(f"{table_name} (colunas ausentes: {', '.join(missing_columns)})")
        
        return problem_tables

    def print_database_schema(self):
        """Imprime o esquema completo do banco de dados."""
        self.stdout.write('\nEsquema do banco de dados:')
        
        with connection.cursor() as cursor:
            # Obtém todas as tabelas
            if connection.vendor == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%';")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in sorted(tables):
                    self.stdout.write(f"\n- Tabela: {table}")
                    
                    # Obtém as colunas da tabela
                    cursor.execute(f"PRAGMA table_info({table});")
                    columns = cursor.fetchall()
                    
                    for column in columns:
                        col_id, name, type_name, not_null, default, pk = column
                        attributes = []
                        if pk:
                            attributes.append("PRIMARY KEY")
                        if not_null:
                            attributes.append("NOT NULL")
                        if default is not None:
                            attributes.append(f"DEFAULT {default}")
                        
                        attr_str = ", ".join(attributes)
                        if attr_str:
                            self.stdout.write(f"  - {name} ({type_name}) [{attr_str}]")
                        else:
                            self.stdout.write(f"  - {name} ({type_name})")
            else:
                self.stdout.write(self.style.WARNING(f"Impressão de esquema não implementada para {connection.vendor}"))
                
        self.stdout.write('')  # Empty line at the end 