from django.core.management.base import BaseCommand
from questionarios.supabase_sync import sync_all_data

class Command(BaseCommand):
    help = 'Sincroniza todos os dados existentes com o Supabase'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando sincronização com o Supabase...'))
        
        try:
            sync_all_data()
            self.stdout.write(self.style.SUCCESS('Sincronização concluída com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro durante a sincronização: {e}')) 