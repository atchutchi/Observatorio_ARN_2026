import os
import sqlite3
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige problemas no banco de dados SQLite, como colunas ausentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Cria um backup do banco de dados antes de fazer alterações',
        )

    def handle(self, *args, **options):
        """Executa o comando para corrigir problemas no banco de dados."""
        
        # Criar backup se solicitado
        if options['backup']:
            self.backup_database()
        
        # Corrigir problemas específicos
        self.fix_estacoes_moveis_columns()
        
        self.stdout.write(
            self.style.SUCCESS('Correções aplicadas com sucesso!')
        )

    def backup_database(self):
        """Cria um backup do banco de dados atual."""
        db_path = settings.DATABASES['default']['NAME']
        if not os.path.exists(db_path):
            self.stdout.write(
                self.style.WARNING(f'O arquivo de banco de dados não foi encontrado: {db_path}')
            )
            return
        
        backup_path = f"{db_path}.bak"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(f'Backup do banco de dados criado em: {backup_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar backup: {str(e)}')
            )

    def fix_estacoes_moveis_columns(self):
        """Corrige a tabela questionarios_estacoesmoveisindicador."""
        self.stdout.write('Corrigindo a tabela questionarios_estacoesmoveisindicador...')
        
        cursor = connection.cursor()
        
        # Verificar se a tabela existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='questionarios_estacoesmoveisindicador'"
        )
        if not cursor.fetchone():
            self.stdout.write(
                self.style.WARNING('A tabela questionarios_estacoesmoveisindicador não existe.')
            )
            return
        
        # Verificar se as colunas existem
        cursor.execute("PRAGMA table_info(questionarios_estacoesmoveisindicador)")
        columns = [column[1] for column in cursor.fetchall()]
        
        missing_columns = []
        
        # Verificar coluna numero_utilizadores e outras colunas essenciais
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
            if col_name not in columns:
                missing_columns.append({
                    'name': col_name,
                    'type': col_type
                })
                self.stdout.write(
                    self.style.WARNING(f'A coluna {col_name} está ausente e será adicionada.')
                )
        
        # Adicionar colunas ausentes
        for column in missing_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE questionarios_estacoesmoveisindicador ADD COLUMN {column['name']} {column['type']}"
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Coluna {column['name']} adicionada com sucesso.")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro ao adicionar coluna {column['name']}: {str(e)}")
                )
        
        if not missing_columns:
            self.stdout.write(
                self.style.SUCCESS('Todas as colunas esperadas já existem na tabela.')
            ) 