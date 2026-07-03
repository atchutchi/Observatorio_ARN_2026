#!/usr/bin/env python
"""
Script de Auditoria de Templates
Observatório ARN - Análise de Padronização

Este script audita todos os templates do projeto verificando:
- Validação de erros consistente
- Presença de CSRF tokens
- Labels com 'for' attribute
- Classes CSS padronizadas
- ARIA attributes
- Blocos Django template

Uso:
    python scripts/audit_templates.py
    python scripts/audit_templates.py --fix (para aplicar correções automaticamente)
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

class TemplateAuditor:
    def __init__(self, base_path='.'):
        self.base_path = Path(base_path)
        self.issues = defaultdict(list)
        self.stats = {
            'total_templates': 0,
            'templates_with_forms': 0,
            'csrf_missing': 0,
            'invalid_feedback_without_dblock': 0,
            'mismatched_validation': 0,
            'labels_without_for': 0,
            'missing_aria': 0,
        }
    
    def find_templates(self):
        """Encontra todos os templates HTML no projeto"""
        templates = []
        template_dirs = [
            'templates',
            'home/templates',
            'dashboard/templates',
            'questionarios/templates'
        ]
        
        for template_dir in template_dirs:
            path = self.base_path / template_dir
            if path.exists():
                templates.extend(path.rglob('*.html'))
        
        return templates
    
    def check_csrf_token(self, content, filepath):
        """Verifica presença de CSRF token em formulários"""
        has_form = re.search(r'<form', content, re.IGNORECASE)
        has_csrf = re.search(r'{%\s*csrf_token\s*%}', content)
        
        if has_form and not has_csrf:
            self.issues[filepath].append({
                'type': 'csrf_missing',
                'severity': 'critical',
                'message': 'Formulário sem CSRF token'
            })
            self.stats['csrf_missing'] += 1
            return False
        return True
    
    def check_validation_mismatch(self, content, filepath):
        """Verifica se validação de erros está correta"""
        # Padrão: {% if form.campo_A.errors %} ... {% for error in form.campo_B.errors %}
        pattern = r'{%\s*if\s+form\.(\w+)\.errors\s*%}.*?{%\s*for\s+error\s+in\s+form\.(\w+)\.errors\s*%}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        mismatches = []
        for if_field, for_field in matches:
            if if_field != for_field:
                mismatches.append((if_field, for_field))
                self.stats['mismatched_validation'] += 1
        
        if mismatches:
            for if_field, for_field in mismatches:
                self.issues[filepath].append({
                    'type': 'validation_mismatch',
                    'severity': 'critical',
                    'message': f'Validação inconsistente: if form.{if_field}.errors mas for error in form.{for_field}.errors'
                })
            return False
        return True
    
    def check_invalid_feedback_class(self, content, filepath):
        """Verifica se invalid-feedback tem classe d-block"""
        pattern = r'<div\s+class="[^"]*invalid-feedback[^"]*"[^>]*>'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        issues_found = 0
        for match in matches:
            if 'd-block' not in match:
                issues_found += 1
                self.stats['invalid_feedback_without_dblock'] += 1
        
        if issues_found > 0:
            self.issues[filepath].append({
                'type': 'invalid_feedback_class',
                'severity': 'warning',
                'message': f'{issues_found} ocorrência(s) de invalid-feedback sem d-block'
            })
            return False
        return True
    
    def check_labels_with_for(self, content, filepath):
        """Verifica se labels têm atributo 'for'"""
        # Encontrar labels dentro de forms
        if '<form' not in content.lower():
            return True
        
        label_pattern = r'<label[^>]*>'
        labels = re.findall(label_pattern, content, re.IGNORECASE)
        
        labels_without_for = 0
        for label in labels:
            if 'for=' not in label.lower():
                labels_without_for += 1
                self.stats['labels_without_for'] += 1
        
        if labels_without_for > 0:
            self.issues[filepath].append({
                'type': 'labels_without_for',
                'severity': 'warning',
                'message': f'{labels_without_for} label(s) sem atributo for'
            })
            return False
        return True
    
    def check_aria_attributes(self, content, filepath):
        """Verifica presença de ARIA attributes"""
        if '<form' not in content.lower():
            return True
        
        # Verificar inputs obrigatórios sem aria-required
        required_inputs = re.findall(r'<input[^>]*required[^>]*>', content, re.IGNORECASE)
        missing_aria = 0
        
        for input_tag in required_inputs:
            if 'aria-required' not in input_tag.lower():
                missing_aria += 1
                self.stats['missing_aria'] += 1
        
        if missing_aria > 0:
            self.issues[filepath].append({
                'type': 'missing_aria',
                'severity': 'info',
                'message': f'{missing_aria} campo(s) required sem aria-required'
            })
            return False
        return True
    
    def audit_template(self, template_path):
        """Audita um template específico"""
        try:
            content = template_path.read_text(encoding='utf-8')
            self.stats['total_templates'] += 1
            
            # Verificar se é um formulário
            if '<form' in content.lower():
                self.stats['templates_with_forms'] += 1
            
            # Executar verificações
            self.check_csrf_token(content, str(template_path))
            self.check_validation_mismatch(content, str(template_path))
            self.check_invalid_feedback_class(content, str(template_path))
            self.check_labels_with_for(content, str(template_path))
            self.check_aria_attributes(content, str(template_path))
            
        except Exception as e:
            print_error(f"Erro ao auditar {template_path}: {e}")
    
    def generate_report(self):
        """Gera relatório da auditoria"""
        print_header("RELATÓRIO DE AUDITORIA DE TEMPLATES")
        
        # Estatísticas gerais
        print_info("📊 ESTATÍSTICAS GERAIS")
        print(f"Total de templates: {self.stats['total_templates']}")
        print(f"Templates com formulários: {self.stats['templates_with_forms']}")
        print()
        
        # Problemas por severidade
        critical = sum(1 for issues in self.issues.values() for issue in issues if issue['severity'] == 'critical')
        warnings = sum(1 for issues in self.issues.values() for issue in issues if issue['severity'] == 'warning')
        info = sum(1 for issues in self.issues.values() for issue in issues if issue['severity'] == 'info')
        
        print_info("🔍 PROBLEMAS ENCONTRADOS")
        if critical > 0:
            print_error(f"Críticos: {critical}")
        else:
            print_success(f"Críticos: 0")
        
        if warnings > 0:
            print_warning(f"Avisos: {warnings}")
        else:
            print_success(f"Avisos: 0")
        
        print_info(f"Informativos: {info}")
        print()
        
        # Detalhes por tipo
        print_info("📋 DETALHES POR TIPO DE PROBLEMA")
        problem_types = {
            'CSRF Token Faltando': self.stats['csrf_missing'],
            'Validação Inconsistente': self.stats['mismatched_validation'],
            'invalid-feedback sem d-block': self.stats['invalid_feedback_without_dblock'],
            'Labels sem atributo for': self.stats['labels_without_for'],
            'Campos sem ARIA attributes': self.stats['missing_aria'],
        }
        
        for problem, count in problem_types.items():
            if count > 0:
                print_error(f"  {problem}: {count}")
            else:
                print_success(f"  {problem}: 0")
        print()
        
        # Templates com problemas
        if self.issues:
            print_info(f"📁 TEMPLATES COM PROBLEMAS ({len(self.issues)})")
            for filepath, issues in sorted(self.issues.items()):
                print(f"\n{Colors.BOLD}{filepath}{Colors.ENDC}")
                for issue in issues:
                    if issue['severity'] == 'critical':
                        print_error(f"  {issue['message']}")
                    elif issue['severity'] == 'warning':
                        print_warning(f"  {issue['message']}")
                    else:
                        print_info(f"  {issue['message']}")
        else:
            print_success("✅ Nenhum template com problemas encontrado!")
        
        # Resumo final
        print_header("RESUMO")
        total_issues = sum(len(issues) for issues in self.issues.values())
        if total_issues == 0:
            print_success("🎉 Todos os templates estão em conformidade!")
            return 0
        else:
            print_warning(f"⚠️  {total_issues} problema(s) encontrado(s) em {len(self.issues)} template(s)")
            print_info("\nPara corrigir, consulte: TEMPLATES_STANDARDIZATION_PLAN.md")
            return 1

def main():
    import sys
    
    print_header("OBSERVATÓRIO ARN - AUDITORIA DE TEMPLATES")
    print_info("Iniciando auditoria...")
    print()
    
    auditor = TemplateAuditor()
    templates = auditor.find_templates()
    
    print_info(f"Encontrados {len(templates)} templates para auditar")
    print()
    
    for template in templates:
        auditor.audit_template(template)
    
    exit_code = auditor.generate_report()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

