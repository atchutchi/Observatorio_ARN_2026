from django.core.management.base import BaseCommand
from django.conf import settings
import os
import re

class Command(BaseCommand):
    help = 'Verifica configurações de segurança da ARN Platform'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔒 VERIFICAÇÃO DE SEGURANÇA ARN PLATFORM')
        )
        self.stdout.write('=' * 50)
        
        security_score = 0
        total_checks = 8
        
        # 1. Verificar SECRET_KEY
        if settings.SECRET_KEY != 'django-insecure-^7mu8809@rhbjdc#ljlr5ra%h#45zx$%0%o@9-fqz(b63nfg&r':
            self.stdout.write(self.style.SUCCESS('✅ SECRET_KEY customizada'))
            security_score += 1
        else:
            self.stdout.write(self.style.ERROR('❌ SECRET_KEY padrão em uso - ALTERE!'))
        
        # 2. Verificar DEBUG
        if not settings.DEBUG:
            self.stdout.write(self.style.SUCCESS('✅ DEBUG desabilitado (produção)'))
            security_score += 1
        else:
            self.stdout.write(self.style.WARNING('⚠️ DEBUG habilitado (desenvolvimento)'))
            security_score += 0.5
        
        # 3. Verificar arquivo .env
        env_path = os.path.join(settings.BASE_DIR, '.env')
        if os.path.exists(env_path):
            self.stdout.write(self.style.SUCCESS('✅ Arquivo .env existe'))
            security_score += 1
            
            # Verificar se tem configurações básicas
            with open(env_path, 'r') as f:
                env_content = f.read()
                
            if 'ADMIN_PASSWORD=' in env_content and 'admin123' not in env_content:
                self.stdout.write(self.style.SUCCESS('✅ Senha de admin configurada'))
                security_score += 1
            else:
                self.stdout.write(self.style.ERROR('❌ Configure ADMIN_PASSWORD no .env'))
                
        else:
            self.stdout.write(self.style.ERROR('❌ Arquivo .env não encontrado - CRIE!'))
        
        # 4. Verificar ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS != ['*']:
            self.stdout.write(self.style.SUCCESS('✅ ALLOWED_HOSTS configurado'))
            security_score += 1
        else:
            self.stdout.write(self.style.WARNING('⚠️ ALLOWED_HOSTS muito permissivo'))
            security_score += 0.5
        
        # 5. Verificar middleware de autenticação
        middleware_classes = [cls.split('.')[-1] for cls in settings.MIDDLEWARE]
        if 'PlatformAuthMiddleware' in middleware_classes:
            self.stdout.write(self.style.SUCCESS('✅ Middleware de autenticação ativo'))
            security_score += 1
        else:
            self.stdout.write(self.style.ERROR('❌ Middleware de autenticação não encontrado'))
        
        # 6. Verificar configuração de email
        if hasattr(settings, 'EMAIL_HOST_PASSWORD'):
            if settings.EMAIL_HOST_PASSWORD and 'ARN/2025' not in str(settings.EMAIL_HOST_PASSWORD):
                self.stdout.write(self.style.SUCCESS('✅ Email configurado com senha segura'))
                security_score += 1
            else:
                self.stdout.write(self.style.ERROR('❌ Senha de email padrão - ALTERE!'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Email usando variáveis de ambiente'))
            security_score += 1
        
        # 7. Verificar database
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(self.style.WARNING('⚠️ Usando SQLite (desenvolvimento)'))
            security_score += 0.5
        else:
            self.stdout.write(self.style.SUCCESS('✅ Database de produção configurado'))
            security_score += 1
        
        # 8. Verificar logs sensíveis
        log_files = ['logs/observatorio.log', 'logs/observatorio_error.log']
        sensitive_found = False
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    content = f.read()
                    if 'admin123' in content or 'ARN/2025' in content:
                        sensitive_found = True
                        
        if not sensitive_found:
            self.stdout.write(self.style.SUCCESS('✅ Logs livres de credenciais'))
            security_score += 1
        else:
            self.stdout.write(self.style.ERROR('❌ Credenciais encontradas em logs - LIMPE!'))
        
        # Calcular score final
        final_score = (security_score / total_checks) * 100
        
        self.stdout.write('\n' + '=' * 50)
        
        if final_score >= 90:
            self.stdout.write(
                self.style.SUCCESS(f'🛡️ SEGURANÇA EXCELENTE: {final_score:.1f}% ({security_score}/{total_checks})')
            )
        elif final_score >= 70:
            self.stdout.write(
                self.style.WARNING(f'⚠️ SEGURANÇA BOA: {final_score:.1f}% ({security_score}/{total_checks})')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'🚨 SEGURANÇA CRÍTICA: {final_score:.1f}% ({security_score}/{total_checks})')
            )
        
        self.stdout.write('\n📋 RECOMENDAÇÕES:')
        self.stdout.write('1. Configure .env com credenciais seguras')
        self.stdout.write('2. Execute: python manage.py create_admin_user --interactive')
        self.stdout.write('3. Altere senhas expostas imediatamente')
        self.stdout.write('4. Configure email de produção com senha de app')
        self.stdout.write('5. Monitore logs por dados sensíveis')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎯 ARN Platform protegida e segura!')
        )
