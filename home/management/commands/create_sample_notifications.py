from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Notification

class Command(BaseCommand):
    help = 'Cria notificações de exemplo para testar o sistema'

    def handle(self, *args, **options):
        # Pegar o primeiro usuário ativo
        users = User.objects.filter(is_active=True)
        if not users.exists():
            self.stdout.write(self.style.WARNING('Nenhum usuário ativo encontrado.'))
            return

        user = users.first()
        
        # Criar notificações de exemplo
        notifications = [
            {
                'title': 'Bem-vindo à ARN Platform!',
                'message': 'Sua plataforma de telecomunicações foi atualizada com um novo design.',
                'notification_type': 'success'
            },
            {
                'title': 'Novos dados carregados',
                'message': 'Os dados de assinantes de dezembro foram atualizados no sistema.',
                'notification_type': 'info'
            },
            {
                'title': 'Sistema de backup',
                'message': 'O backup automático será executado às 02:00 da madrugada.',
                'notification_type': 'warning'
            },
            {
                'title': 'Relatório mensal',
                'message': 'O relatório mensal de telecomunicações está pronto para download.',
                'notification_type': 'info'
            },
            {
                'title': 'Manutenção programada',
                'message': 'Haverá manutenção no sistema no próximo domingo das 01:00 às 03:00.',
                'notification_type': 'warning'
            }
        ]

        created_count = 0
        for notification_data in notifications:
            # Verificar se já existe uma notificação similar
            exists = Notification.objects.filter(
                user=user,
                title=notification_data['title']
            ).exists()
            
            if not exists:
                Notification.objects.create(
                    user=user,
                    **notification_data
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Criadas {created_count} notificações para o usuário {user.email}'
            )
        )
