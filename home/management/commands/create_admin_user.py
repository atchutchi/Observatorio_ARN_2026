import getpass
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError


class Command(BaseCommand):
    help = (
        'Cria ou atualiza um administrador usando ADMIN_USERNAME, ADMIN_EMAIL '
        'e ADMIN_PASSWORD, ou parâmetros de linha de comando.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário do administrador')
        parser.add_argument('--email', type=str, help='Email do administrador')
        parser.add_argument('--password', type=str, help='Senha do administrador (prefira ADMIN_PASSWORD em produção)')
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='Atualiza a senha se o usuário já existir',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Pergunta os dados no terminal, sem ecoar a senha',
        )

    def handle(self, *args, **options):
        username, email, password = self._get_credentials(options)
        User = get_user_model()

        existing_user = (
            User.objects.filter(username=username).first()
            or User.objects.filter(email__iexact=email).first()
        )

        if existing_user:
            self._update_existing_user(existing_user, username, email, password, options['reset_password'])
            return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        except IntegrityError as exc:
            raise CommandError(f'Erro ao criar usuário: {exc}') from exc

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Superuser "{user.username}" criado com sucesso.\n'
                f'📧 Email: {user.email}\n'
                '🔑 Acesse /accounts/login/ com o email ou /admin/ com o username.'
            )
        )

    def _get_credentials(self, options):
        if options['interactive']:
            username = input('Username: ').strip()
            email = input('Email: ').strip()
            password = getpass.getpass('Password: ')
        else:
            username = (options.get('username') or os.getenv('ADMIN_USERNAME') or '').strip()
            email = (options.get('email') or os.getenv('ADMIN_EMAIL') or '').strip()
            password = options.get('password') or os.getenv('ADMIN_PASSWORD') or ''

        missing = [name for name, value in (('username', username), ('email', email), ('password', password)) if not value]
        if missing:
            raise CommandError(
                'Faltam dados: ' + ', '.join(missing) + '. '
                'Use ADMIN_USERNAME, ADMIN_EMAIL e ADMIN_PASSWORD, passe os parâmetros, '
                'ou execute com --interactive.'
            )
        return username, email, password

    def _update_existing_user(self, user, username, email, password, reset_password):
        changed_fields = []

        if user.username != username:
            user.username = username
            changed_fields.append('username')
        if user.email != email:
            user.email = email
            changed_fields.append('email')
        if not user.is_staff:
            user.is_staff = True
            changed_fields.append('is_staff')
        if not user.is_superuser:
            user.is_superuser = True
            changed_fields.append('is_superuser')
        if reset_password:
            user.set_password(password)
            changed_fields.append('password')

        if changed_fields:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Administrador "{user.username}" atualizado: {", ".join(changed_fields)}.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Usuário "{user.username}" já existe. Use --reset-password para trocar a senha.'
                )
            )
