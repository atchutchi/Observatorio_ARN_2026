#!/usr/bin/env python3
"""
Script para substituir todas as referências TELECEL por TELECEL
e atualizar cores para vermelho
"""

import os
import re
import glob

def find_and_replace_in_file(file_path, replacements):
    """Substitui múltiplas strings em um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        original_content = content
        
        for old_text, new_text in replacements.items():
            content = content.replace(old_text, new_text)
        
        # Se houve mudanças, salvar o arquivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def main():
    print("🔄 Substituindo referências TELECEL por TELECEL...")
    
    # Definir substituições
    replacements = {
        # Nomes de operadoras
        '"TELECEL"': '"TELECEL"',
        "'TELECEL'": "'TELECEL'",
        '>TELECEL<': '>TELECEL<',
        ' TELECEL ': ' TELECEL ',
        'TELECEL:': 'TELECEL:',
        'TELECEL,': 'TELECEL,',
        'TELECEL)': 'TELECEL)',
        '(TELECEL': '(TELECEL',
        'TELECEL vs': 'TELECEL vs',
        'vs TELECEL': 'vs TELECEL',
        'TELECEL e ': 'TELECEL e ',
        ' e TELECEL': ' e TELECEL',
        'da TELECEL': 'da TELECEL',
        'TELECEL.': 'TELECEL.',
        
        # Cores azuis para vermelhas (TELECEL)
        '#DC3545': '#DC3545',  # Azul para vermelho
        '#DC3545': '#DC3545',  # Amarelo TELECEL para vermelho TELECEL
        'color: #DC3545': 'color: #DC3545',
        'background-color: #DC3545': 'background-color: #DC3545',
        'rgba(220, 53, 69': 'rgba(220, 53, 69',
        
        # Referências específicas
        'TELECEL Red': 'TELECEL Red',
        'telecel': 'telecel',
        'Telecel': 'Telecel',
        
        # Comentários e descrições
        'operadora TELECEL': 'operadora TELECEL',
        'Operadora TELECEL': 'Operadora TELECEL',
        'TELECEL Bissau': 'TELECEL Bissau',
        'rede TELECEL': 'rede TELECEL',
        'para TELECEL': 'para TELECEL',
        'da/o TELECEL': 'da/o TELECEL',
    }
    
    # Tipos de arquivos para processar
    file_patterns = [
        '**/*.py',
        '**/*.html', 
        '**/*.css',
        '**/*.js',
        '**/*.md',
    ]
    
    # Diretórios para ignorar
    ignore_patterns = [
        '**/migrations/**',
        '**/staticfiles/**',
        '**/__pycache__/**',
        '**/node_modules/**',
        '.git/**',
    ]
    
    updated_files = []
    
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # Verificar se deve ignorar
            if any(re.match(ignore_pat.replace('**', '.*').replace('*', '[^/]*'), file_path) 
                   for ignore_pat in ignore_patterns):
                continue
                
            if find_and_replace_in_file(file_path, replacements):
                updated_files.append(file_path)
                print(f"✅ Atualizado: {file_path}")
    
    print(f"\n🎉 Concluído! {len(updated_files)} arquivos atualizados.")
    print("\n📋 Resumo das alterações:")
    print("- TELECEL → TELECEL em todos os contextos")
    print("- Cores azuis (#DC3545) → Vermelho (#DC3545)")
    print("- Cores amarelas TELECEL (#DC3545) → Vermelho TELECEL (#DC3545)")
    print("- Referências em templates, CSS, JS e Python")
    
    if updated_files:
        print(f"\n📂 Arquivos alterados:")
        for file_path in updated_files[:10]:  # Mostrar primeiros 10
            print(f"  - {file_path}")
        if len(updated_files) > 10:
            print(f"  ... e mais {len(updated_files) - 10} arquivos")

if __name__ == "__main__":
    main()
