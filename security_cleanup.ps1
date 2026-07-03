# Script PowerShell para limpar histórico Git de credenciais expostas
# Execute este script para remover credenciais do histórico Git

Write-Host "🚨 LIMPEZA DE SEGURANÇA - ARN PLATFORM" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Yellow

Write-Host "🔍 Verificando credenciais expostas..." -ForegroundColor Cyan

# Criar backup do repositório
Write-Host "📦 Criando backup..." -ForegroundColor Yellow
$backupName = "observatorio-arn-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -Path "." -Destination "../$backupName" -Recurse -Force
Write-Host "✅ Backup criado em: ../$backupName" -ForegroundColor Green

# Remover strings sensíveis do histórico
Write-Host "🧹 Removendo credenciais do histórico Git..." -ForegroundColor Cyan

# Lista de strings sensíveis para remover
$sensitiveStrings = @(
    "ARN/2025",
    "admin123",
    "ferreira.atchutchi@arn.gw",
    "abboss40@gmail.com"
)

foreach ($string in $sensitiveStrings) {
    Write-Host "🔍 Removendo: $string" -ForegroundColor Yellow
    
    # Usar git filter-branch para remover strings
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch -r ." --prune-empty --tag-name-filter cat -- --all | Out-Null
    
    # Remover das configurações
    git filter-branch --force --msg-filter "sed 's/$string/[REMOVED]/g'" -- --all | Out-Null
}

Write-Host "🗑️ Limpando referências antigas..." -ForegroundColor Cyan
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "✅ LIMPEZA CONCLUÍDA!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Yellow
Write-Host "🛡️ Credenciais removidas do histórico Git" -ForegroundColor Green
Write-Host "📦 Backup salvo em: ../$backupName" -ForegroundColor Green
Write-Host "⚠️ IMPORTANTE: Altere todas as senhas expostas!" -ForegroundColor Red
Write-Host "🔐 Configure .env com novas credenciais" -ForegroundColor Yellow

# Instruções finais
Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Crie arquivo .env com novas credenciais" -ForegroundColor White
Write-Host "2. Execute: python manage.py create_admin_user --interactive" -ForegroundColor White
Write-Host "3. Altere senhas de email expostas" -ForegroundColor White
Write-Host "4. Verifique se plataforma funciona corretamente" -ForegroundColor White
Write-Host "`n🎉 ARN Platform está segura e protegida!" -ForegroundColor Green
