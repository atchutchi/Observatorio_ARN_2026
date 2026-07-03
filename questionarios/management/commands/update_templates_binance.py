from django.core.management.base import BaseCommand
import os
import glob

class Command(BaseCommand):
    help = 'Atualiza templates antigos para usar tema Binance'

    def handle(self, *args, **options):
        templates_dir = 'questionarios/templates/questionarios/'
        
        # Templates que precisam ser atualizados
        templates_to_update = [
            'receitas_form.html',
            'receitas_detail.html', 
            'receitas_confirm_delete.html',
            'investimento_form.html',
            'investimento_detail.html',
            'investimento_confirm_delete.html',
            'emprego_form.html',
            'emprego_detail.html',
            'emprego_delete.html',
            'trafego_originado_form.html',
            'trafego_originado_detail.html',
            'trafego_originado_confirm_delete.html',
            'trafego_terminado_form.html',
            'trafego_terminado_detail.html',
            'trafego_terminado_confirm_delete.html',
            'trafego_roaming_internacional_form.html',
            'trafego_roaming_internacional_detail.html',
            'trafego_roaming_internacional_confirm_delete.html',
            'lbi_form.html',
            'lbi_detail.html',
            'lbi_confirm_delete.html',
            'trafego_internet_form.html',
            'trafego_internet_detail.html',
            'trafego_internet_confirm_delete.html',
            'internet_fixo_form.html',
            'internet_fixo_detail.html',
            'internet_fixo_confirm_delete.html',
            'tarifario_orange_form.html',
            'tarifario_orange_detail.html',
            'tarifario_orange_confirm_delete.html',
            'tarifario_telecel_form.html',
            'tarifario_telecel_detail.html',
            'tarifario_telecel_confirm_delete.html',
            'tarifario_telecel_form.html',
            'tarifario_telecel_detail.html',
            'tarifario_telecel_confirm_delete.html'
        ]
        
        updated_count = 0
        
        for template_name in templates_to_update:
            template_path = os.path.join(templates_dir, template_name)
            
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar se já usa tema Binance
                    if 'questionarios/base_questionarios.html' in content or 'questionarios/partials/base' in content:
                        self.stdout.write(f'⏭️  {template_name} já usa tema Binance')
                        continue
                    
                    # Determinar tipo de template
                    if '_form.html' in template_name:
                        new_content = self.create_form_template(template_name, content)
                    elif '_detail.html' in template_name:
                        new_content = self.create_detail_template(template_name, content)
                    elif 'confirm_delete.html' in template_name or '_delete.html' in template_name:
                        new_content = self.create_delete_template(template_name, content)
                    else:
                        continue
                    
                    # Salvar template atualizado
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Atualizado: {template_name}')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erro ao atualizar {template_name}: {e}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Não encontrado: {template_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Concluído! {updated_count} templates atualizados para tema Binance.'
            )
        )
    
    def create_form_template(self, template_name, original_content):
        """Cria template de formulário com tema Binance"""
        indicator_name = template_name.replace('_form.html', '')
        
        return f'''{{%% extends "questionarios/partials/base_form.html" %%}}
{{%% load static %%}}

{{%% block form_title %%}}{{%% if form.instance.pk %%}}Editar{{%% else %%}}Criar{{%% endif %%}} Indicador de {indicator_name.replace('_', ' ').title()}{{%% endblock %%}}
{{%% block form_subtitle %%}}Gestão de dados de {indicator_name.replace('_', ' ')} por operadora{{%% endblock %%}}

{{%% block list_url %%}}{{%% url 'questionarios:{indicator_name}_list' %%}}{{%% endblock %%}}

{{%% block form_fields %%}}
<!-- Campos específicos do formulário -->
<div class="platform-card mb-4">
    <div class="card-header">
        <h4 class="card-title">
            <i class="fas fa-edit me-2"></i>
            Dados do Indicador
        </h4>
    </div>
    <div class="card-body">
        <div class="alert-questionario alert-questionario-info">
            <i class="fas fa-info-circle"></i>
            <span>Template gerado automaticamente. Personalize os campos conforme necessário.</span>
        </div>
        
        <!-- Campos do formulário aqui -->
        <div class="row">
            {{{{ form.as_p }}}}
        </div>
    </div>
</div>
{{%% endblock %%}}

{{%% block submit_text %%}}{{%% if form.instance.pk %%}}Atualizar{{%% else %%}}Criar{{%% endif %%}} {indicator_name.replace('_', ' ').title()}{{%% endblock %%}}'''
    
    def create_detail_template(self, template_name, original_content):
        """Cria template de detalhes com tema Binance"""
        indicator_name = template_name.replace('_detail.html', '')
        
        return f'''{{%% extends "questionarios/partials/base_detail.html" %%}}
{{%% load static %%}}

{{%% block detail_title %%}}Detalhes de {indicator_name.replace('_', ' ').title()}{{%% endblock %%}}
{{%% block detail_subtitle %%}}{{{{ object.operadora }}}} - {{{{ object.ano }}}}/{{{{ object.trimestre }}}}º Trimestre{{%% endblock %%}}

{{%% block list_url %%}}{{%% url 'questionarios:{indicator_name}_list' %%}}{{%% endblock %%}}
{{%% block edit_url %%}}{{%% url 'questionarios:{indicator_name}_update' object.pk %%}}{{%% endblock %%}}
{{%% block delete_url %%}}{{%% url 'questionarios:{indicator_name}_delete' object.pk %%}}{{%% endblock %%}}

{{%% block detail_content %%}}
<!-- Dados específicos do indicador -->
<div class="alert-questionario alert-questionario-info">
    <i class="fas fa-info-circle"></i>
    <span>Template gerado automaticamente. Personalize a exibição dos dados conforme necessário.</span>
</div>

<div class="table-responsive">
    <table class="questionario-table">
        <tbody>
            <!-- Adicione aqui os campos específicos do modelo -->
            <tr>
                <td><strong>Dados:</strong></td>
                <td>Personalize este template com os campos específicos do modelo</td>
            </tr>
        </tbody>
    </table>
</div>
{{%% endblock %%}}'''
    
    def create_delete_template(self, template_name, original_content):
        """Cria template de exclusão com tema Binance"""
        indicator_name = template_name.replace('_confirm_delete.html', '').replace('_delete.html', '')
        
        return f'''{{%% extends "questionarios/base_questionarios.html" %%}}
{{%% load static %%}}

{{%% block questionario_title %%}}Confirmar Exclusão{{%% endblock %%}}

{{%% block questionario_content %%}}
<!-- Header de Confirmação -->
<div class="questionario-header">
    <div class="text-center">
        <h1 class="questionario-title">
            <i class="fas fa-exclamation-triangle me-2"></i>
            Confirmar Exclusão
        </h1>
        <p class="questionario-subtitle">Esta ação não pode ser desfeita</p>
    </div>
</div>

<!-- Informações do Item -->
<div class="platform-card mb-4">
    <div class="card-header">
        <h3 class="card-title">
            <i class="fas fa-info-circle me-2"></i>
            Item a Ser Excluído
        </h3>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-4">
                <div class="detail-info-item">
                    <div class="detail-info-icon">
                        {{%% if object.operadora == 'ORANGE' %%}}
                            <i class="fas fa-signal" style="color: #FF6600;"></i>
                        {{%% elif object.operadora == 'TELECEL' %%}}
                            <i class="fas fa-broadcast-tower" style="color: #DC3545;"></i>
                        {{%% else %%}}
                            <i class="fas fa-tower-cell"></i>
                        {{%% endif %%}}
                    </div>
                    <div class="detail-info-content">
                        <strong>Operadora</strong>
                        <p class="operadora-badge {{{{ object.operadora|lower }}}}">{{{{ object.operadora }}}}</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="detail-info-item">
                    <div class="detail-info-icon">
                        <i class="fas fa-calendar"></i>
                    </div>
                    <div class="detail-info-content">
                        <strong>Período</strong>
                        <p>{{{{ object.ano }}}} - {{{{ object.trimestre }}}}º Trimestre</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="detail-info-item">
                    <div class="detail-info-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <div class="detail-info-content">
                        <strong>Tipo</strong>
                        <p>{indicator_name.replace('_', ' ').title()}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Aviso -->
<div class="platform-card mb-4">
    <div class="card-body">
        <div class="alert-questionario alert-questionario-danger">
            <i class="fas fa-exclamation-triangle"></i>
            <div>
                <strong>⚠️ ATENÇÃO!</strong>
                <p class="mt-2 mb-0">
                    Todos os dados relacionados a este indicador serão perdidos permanentemente.
                    Esta ação não pode ser desfeita.
                </p>
            </div>
        </div>
    </div>
</div>

<!-- Botões -->
<div class="platform-card">
    <div class="card-body">
        <form method="post" class="text-center">
            {{%% csrf_token %%}}
            
            <div class="d-flex gap-3 justify-content-center">
                <a href="{{%% url 'questionarios:{indicator_name}_list' %%}}" class="btn btn-outline">
                    <i class="fas fa-arrow-left me-2"></i>Cancelar
                </a>
                
                <button type="submit" class="btn btn-danger">
                    <i class="fas fa-trash me-2"></i>Confirmar Exclusão
                </button>
            </div>
        </form>
    </div>
</div>
{{%% endblock %%}}'''
