import logging
from django.core.management.base import BaseCommand
from observatorio.utils.orm_monitor import diagnose_all_models, diagnose_model
from django.apps import apps

logger = logging.getLogger('observatorio.models')

class Command(BaseCommand):
    help = 'Diagnóstico de modelos para identificar problemas na estrutura do banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_model',
            nargs='?',
            help='Aplicação ou modelo específico para diagnóstico (formato: app_name ou app_name.model_name)',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostrar detalhes completos de cada modelo',
        )

    def handle(self, *args, **options):
        app_model = options.get('app_model')
        detailed = options.get('detailed', False)
        
        if app_model:
            # Diagnóstico específico para uma aplicação ou modelo
            parts = app_model.split('.')
            
            if len(parts) == 1:
                # É uma aplicação
                self.diagnose_app(parts[0], detailed)
            elif len(parts) == 2:
                # É um modelo específico
                self.diagnose_specific_model(parts[0], parts[1], detailed)
            else:
                self.stdout.write(
                    self.style.ERROR('Formato inválido. Use app_name ou app_name.model_name')
                )
        else:
            # Diagnóstico completo de todos os modelos
            self.stdout.write('Iniciando diagnóstico de todos os modelos...')
            models_with_issues = diagnose_all_models()
            
            if models_with_issues:
                self.stdout.write(
                    self.style.WARNING(f'Foram encontrados problemas em {len(models_with_issues)} modelos:')
                )
                for model in models_with_issues:
                    self.stdout.write(f'  - {model}')
            else:
                self.stdout.write(
                    self.style.SUCCESS('Todos os modelos estão OK!')
                )

    def diagnose_app(self, app_name, detailed):
        """Diagnóstico de todos os modelos de uma aplicação"""
        self.stdout.write(f'Analisando modelos da aplicação: {app_name}')
        
        try:
            app = apps.get_app_config(app_name)
            models_with_issues = []
            
            for model in app.get_models():
                self.stdout.write(f'Analisando modelo: {model.__name__}')
                if not diagnose_model(model):
                    models_with_issues.append(model.__name__)
                    
                if detailed:
                    self._print_model_details(model)
            
            if models_with_issues:
                self.stdout.write(
                    self.style.WARNING(f'Foram encontrados problemas em {len(models_with_issues)} modelos:')
                )
                for model in models_with_issues:
                    self.stdout.write(f'  - {model}')
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Todos os modelos da aplicação {app_name} estão OK!')
                )
                
        except LookupError:
            self.stdout.write(
                self.style.ERROR(f'Aplicação não encontrada: {app_name}')
            )

    def diagnose_specific_model(self, app_name, model_name, detailed):
        """Diagnóstico de um modelo específico"""
        self.stdout.write(f'Analisando modelo: {app_name}.{model_name}')
        
        try:
            app = apps.get_app_config(app_name)
            
            try:
                model = app.get_model(model_name)
                
                if diagnose_model(model):
                    self.stdout.write(
                        self.style.SUCCESS(f'Modelo {model.__name__} está OK!')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Foram encontrados problemas no modelo {model.__name__}')
                    )
                
                if detailed:
                    self._print_model_details(model)
                    
            except LookupError:
                self.stdout.write(
                    self.style.ERROR(f'Modelo não encontrado: {model_name}')
                )
                
        except LookupError:
            self.stdout.write(
                self.style.ERROR(f'Aplicação não encontrada: {app_name}')
            )

    def _print_model_details(self, model):
        """Mostra detalhes de um modelo"""
        self.stdout.write('\nDetalhes do modelo:')
        self.stdout.write(f'  - Nome: {model.__name__}')
        self.stdout.write(f'  - Tabela: {model._meta.db_table}')
        
        # Campos
        self.stdout.write('\n  Campos:')
        for field in model._meta.fields:
            self.stdout.write(f'    - {field.name} ({field.__class__.__name__}): {field.column}')
        
        # Relações
        related_fields = []
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                related_fields.append((field.name, field.related_model.__name__))
        
        if related_fields:
            self.stdout.write('\n  Relações:')
            for name, related_model in related_fields:
                self.stdout.write(f'    - {name} -> {related_model}')
        
        # Meta
        meta = model._meta
        self.stdout.write('\n  Meta:')
        self.stdout.write(f'    - Verbose name: {meta.verbose_name}')
        self.stdout.write(f'    - Abstract: {meta.abstract}')
        self.stdout.write(f'    - Managed: {meta.managed}')
        self.stdout.write(f'    - App label: {meta.app_label}')
        
        # Índices
        if meta.indexes:
            self.stdout.write('\n  Índices:')
            for idx in meta.indexes:
                self.stdout.write(f'    - {idx.name}: {", ".join(idx.fields)}')
            
        # Constraints
        if meta.constraints:
            self.stdout.write('\n  Constraints:')
            for constraint in meta.constraints:
                self.stdout.write(f'    - {constraint.name}: {constraint.__class__.__name__}')
                
        self.stdout.write('')  # Empty line at the end 