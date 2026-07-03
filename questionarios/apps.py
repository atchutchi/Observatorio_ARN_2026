from django.apps import AppConfig


class QuestionariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'questionarios'

    def ready(self):
        """
        Registra os sinais para sincronização com o Supabase
        """
        # Importar sinais
        import questionarios.supabase_sync
