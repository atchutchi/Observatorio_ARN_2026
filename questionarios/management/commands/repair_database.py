import os
import logging
import time
from django.core.management.base import BaseCommand
from django.db import connection, utils
from django.conf import settings
from observatorio.utils.db_utils import check_table_exists, check_column_exists

logger = logging.getLogger('observatorio.migrations')

class Command(BaseCommand):
    help = 'Repara problemas no banco de dados criando tabelas e colunas ausentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Cria um backup do banco de dados antes de fazer alterações',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação de tabelas mesmo se elas já existirem',
        )
        parser.add_argument(
            '--skip-check',
            action='store_true',
            help='Pula a verificação prévia e executa diretamente as correções',
        )

    def handle(self, *args, **options):
        """Executa o comando para reparar o banco de dados."""
        start_time = time.time()
        self.stdout.write('Iniciando reparação do banco de dados...')
        
        # Criar backup se solicitado
        if options['backup']:
            self.backup_database()
        
        # Verificar problemas conhecidos
        if not options['skip_check']:
            problem_tables = self.check_known_issues()
            if not problem_tables and not options['force']:
                self.stdout.write(
                    self.style.SUCCESS('Nenhum problema conhecido encontrado. Utilize --force para executar as correções mesmo assim.')
                )
                return
        
        # Executar migrações pendentes
        self.apply_migrations()
        
        # Corrigir problemas específicos em tabelas
        self.fix_missing_tables(force=options['force'])
        self.fix_estacoes_moveis_columns()
        self.fix_trafego_originado_table()
        self.fix_investimento_table()
        
        # Sincronizar modelos
        self.sync_models()
        
        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Reparação do banco de dados concluída em {elapsed_time:.2f} segundos!')
        )

    def backup_database(self):
        """Cria um backup do banco de dados atual."""
        db_path = settings.DATABASES['default']['NAME']
        if not os.path.exists(db_path):
            self.stdout.write(
                self.style.WARNING(f'O arquivo de banco de dados não foi encontrado: {db_path}')
            )
            return
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = f"{db_path}.{timestamp}.bak"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(f'Backup do banco de dados criado em: {backup_path}')
            )
            logger.info(f'Backup do banco de dados criado: {backup_path}')
        except Exception as e:
            error_msg = f'Erro ao criar backup: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)

    def check_known_issues(self):
        """Verifica se existem problemas conhecidos no banco de dados."""
        problem_tables = []
        
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
            if not check_table_exists(table_name):
                problem_tables.append(f"{table_name} (tabela ausente)")
                continue
            
            if columns:
                missing_columns = []
                for column in columns:
                    if not check_column_exists(table_name, column):
                        missing_columns.append(column)
                
                if missing_columns:
                    problem_tables.append(f"{table_name} (colunas ausentes: {', '.join(missing_columns)})")
        
        if problem_tables:
            self.stdout.write(
                self.style.WARNING(f'Foram encontrados problemas em {len(problem_tables)} tabelas:')
            )
            for table in problem_tables:
                self.stdout.write(f"  - {table}")
        
        return problem_tables

    def apply_migrations(self):
        """Aplica migrações pendentes."""
        self.stdout.write('Aplicando migrações pendentes...')
        try:
            from django.core.management import call_command
            call_command('migrate', interactive=False)
            self.stdout.write(self.style.SUCCESS('Migrações aplicadas com sucesso.'))
        except Exception as e:
            error_msg = f'Erro ao aplicar migrações: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)

    def fix_missing_tables(self, force=False):
        """Cria tabelas ausentes."""
        missing_tables = [
            'questionarios_trafegooriginadoindicador',
            'questionarios_investimentoindicador'
        ]
        
        for table_name in missing_tables:
            if force or not check_table_exists(table_name):
                self.stdout.write(f'Criando tabela {table_name}...')
                self.create_table(table_name)
    
    def create_table(self, table_name):
        """Cria uma tabela específica baseada no nome."""
        cursor = connection.cursor()
        
        try:
            if table_name == 'questionarios_trafegooriginadoindicador':
                cursor.execute("""
                CREATE TABLE "questionarios_trafegooriginadoindicador" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "ano" integer NOT NULL,
                    "mes" integer NOT NULL,
                    "chamadas_on_net" integer NOT NULL DEFAULT 0,
                    "duracao_on_net" integer NOT NULL DEFAULT 0,
                    "chamadas_off_net" integer NOT NULL DEFAULT 0,
                    "duracao_off_net" integer NOT NULL DEFAULT 0,
                    "chamadas_fixo" integer NOT NULL DEFAULT 0,
                    "duracao_fixo" integer NOT NULL DEFAULT 0,
                    "chamadas_internacional" integer NOT NULL DEFAULT 0,
                    "duracao_internacional" integer NOT NULL DEFAULT 0,
                    "chamadas_servicos_especiais" integer NOT NULL DEFAULT 0,
                    "duracao_servicos_especiais" integer NOT NULL DEFAULT 0,
                    "sms_on_net" integer NOT NULL DEFAULT 0,
                    "sms_off_net" integer NOT NULL DEFAULT 0,
                    "sms_internacional" integer NOT NULL DEFAULT 0,
                    "data_criacao" datetime NOT NULL,
                    "data_atualizacao" datetime NOT NULL,
                    "criado_por_id" integer,
                    "operadora_id" integer NOT NULL,
                    "atualizado_por_id" integer,
                    FOREIGN KEY ("criado_por_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                    FOREIGN KEY ("operadora_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                    FOREIGN KEY ("atualizado_por_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
                );
                """)
                
                self.stdout.write(self.style.SUCCESS(f'Tabela questionarios_trafegooriginadoindicador criada com sucesso.'))
                
            elif table_name == 'questionarios_investimentoindicador':
                cursor.execute("""
                CREATE TABLE "questionarios_investimentoindicador" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "ano" integer NOT NULL,
                    "mes" integer NOT NULL,
                    "infraestrutura_rede" decimal(20, 2) NOT NULL DEFAULT 0,
                    "plataformas_servicos" decimal(20, 2) NOT NULL DEFAULT 0,
                    "equipamentos_informaticos" decimal(20, 2) NOT NULL DEFAULT 0,
                    "licencas_software" decimal(20, 2) NOT NULL DEFAULT 0,
                    "pesquisa_desenvolvimento" decimal(20, 2) NOT NULL DEFAULT 0,
                    "outros_investimentos" text NULL,
                    "data_criacao" datetime NOT NULL,
                    "data_atualizacao" datetime NOT NULL,
                    "criado_por_id" integer,
                    "operadora_id" integer NOT NULL,
                    "atualizado_por_id" integer,
                    FOREIGN KEY ("criado_por_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                    FOREIGN KEY ("operadora_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                    FOREIGN KEY ("atualizado_por_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
                );
                """)
                
                self.stdout.write(self.style.SUCCESS(f'Tabela questionarios_investimentoindicador criada com sucesso.'))
                
            else:
                self.stdout.write(self.style.WARNING(f'Definição não encontrada para a tabela {table_name}.'))
                
        except utils.Error as e:
            error_msg = f'Erro ao criar tabela {table_name}: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)

    def fix_estacoes_moveis_columns(self):
        """Corrige a tabela questionarios_estacoesmoveisindicador."""
        self.stdout.write('Corrigindo a tabela questionarios_estacoesmoveisindicador...')
        
        if not check_table_exists('questionarios_estacoesmoveisindicador'):
            self.stdout.write(
                self.style.WARNING('A tabela questionarios_estacoesmoveisindicador não existe.')
            )
            return
        
        cursor = connection.cursor()
        
        # Verificar colunas essenciais
        all_required_columns = {
            'numero_utilizadores': 'integer NOT NULL DEFAULT 0',
            'numero_utilizadores_mulher': 'integer NOT NULL DEFAULT 0',
            'numero_utilizadores_homem': 'integer NOT NULL DEFAULT 0',
            'total_carregamentos': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_carregamentos_mulher': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_carregamentos_homem': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_levantamentos': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_levantamentos_mulher': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_levantamentos_homem': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_transferencias': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_transferencias_mulher': 'decimal(20,2) NOT NULL DEFAULT 0',
            'total_transferencias_homem': 'decimal(20,2) NOT NULL DEFAULT 0'
        }
        
        for col_name, col_type in all_required_columns.items():
            if not check_column_exists('questionarios_estacoesmoveisindicador', col_name):
                try:
                    cursor.execute(
                        f"ALTER TABLE questionarios_estacoesmoveisindicador ADD COLUMN {col_name} {col_type}"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Coluna {col_name} adicionada com sucesso.")
                    )
                    logger.info(f"Coluna {col_name} adicionada à tabela questionarios_estacoesmoveisindicador")
                except Exception as e:
                    error_msg = f"Erro ao adicionar coluna {col_name}: {str(e)}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    logger.error(error_msg)

    def fix_trafego_originado_table(self):
        """Verifica e corrige a tabela questionarios_trafegooriginadoindicador."""
        if not check_table_exists('questionarios_trafegooriginadoindicador'):
            self.stdout.write(
                self.style.WARNING('A tabela questionarios_trafegooriginadoindicador não existe para ser corrigida.')
            )
            return
            
        self.stdout.write('Verificando a tabela questionarios_trafegooriginadoindicador...')
        # Verificações adicionais podem ser implementadas aqui

    def fix_investimento_table(self):
        """Verifica e corrige a tabela questionarios_investimentoindicador."""
        if not check_table_exists('questionarios_investimentoindicador'):
            self.stdout.write(
                self.style.WARNING('A tabela questionarios_investimentoindicador não existe para ser corrigida.')
            )
            return
            
        self.stdout.write('Verificando a tabela questionarios_investimentoindicador...')
        # Verificações adicionais podem ser implementadas aqui

    def sync_models(self):
        """Sincroniza os modelos com o banco de dados."""
        self.stdout.write('Sincronizando modelos com o banco de dados...')
        try:
            from django.core.management import call_command
            call_command('makemigrations', interactive=False)
            call_command('migrate', interactive=False)
            self.stdout.write(self.style.SUCCESS('Modelos sincronizados com sucesso.'))
        except Exception as e:
            error_msg = f'Erro ao sincronizar modelos: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg) 