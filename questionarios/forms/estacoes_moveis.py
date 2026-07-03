from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models.estacoes_moveis import EstacoesMoveisIndicador

class EstacoesMoveisForm(forms.ModelForm):
    """
    Formulário para Estações Móveis baseado na estrutura KPI ARN.
    Inclui validações complexas e formatação para valores grandes.
    """
    
    class Meta:
        model = EstacoesMoveisIndicador
        fields = [
            # Dados básicos
            'ano', 'mes', 'operadora',
            
            # SEÇÃO 1: ESTAÇÕES MÓVEIS ATIVAS
            'afectos_planos_pos_pagos', 'afectos_planos_pos_pagos_utilizacao',
            'afectos_planos_pre_pagos', 'afectos_planos_pre_pagos_utilizacao',
            'associados_situacoes_especificas', 'outros_residuais',
            
            # SEÇÃO 2: UTILIZADORES DE SERVIÇOS
            # 2.1 Serviços básicos
            'sms', 'mms', 'mobile_tv', 'roaming_internacional_out_parc_roaming_out',
            
            # 2.1.5 Banda larga 3G
            'utilizadores_servico_3g_upgrades',
            'utilizadores_acesso_internet_3g',
            'utilizadores_3g_placas_box',
            'utilizadores_3g_placas_usb',
            
            # 2.1.5 Banda larga 4G
            'utilizadores_servico_4g',
            'utilizadores_acesso_internet_4g',
            'utilizadores_4g_placas_box',
            'utilizadores_4g_placas_usb',
            
            # SEÇÃO 3: MOBILE MONEY
            'numero_utilizadores', 'numero_utilizadores_mulher', 'numero_utilizadores_homem',
            'total_carregamentos', 'total_carregamentos_mulher', 'total_carregamentos_homem',
            'total_levantamentos', 'total_levantamentos_mulher', 'total_levantamentos_homem',
            'total_transferencias', 'total_transferencias_mulher', 'total_transferencias_homem',
            
            # SEÇÃO 4: LINHAS ALUGADAS
            'linhas_64kbit', 'linhas_128kbit', 'linhas_256kbit',
            'linhas_512kbit', 'linhas_1mbit', 'linhas_maior_2mbit'
        ]
        
        widgets = {
            'ano': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030',
                'placeholder': 'Ano'
            }),
            'mes': forms.Select(attrs={'class': 'form-control'}),
            'operadora': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurações gerais para todos os campos
        for field_name, field in self.fields.items():
            # Adicionar classe form-control
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control-questionario'
            else:
                field.widget.attrs['class'] = 'form-control form-control-questionario'
        
        # ========== SEÇÃO 1: ESTAÇÕES MÓVEIS ==========
        self._configure_estacoes_moveis_fields()
        
        # ========== SEÇÃO 2: SERVIÇOS ==========
        self._configure_servicos_fields()
        
        # ========== SEÇÃO 3: MOBILE MONEY ==========
        self._configure_mobile_money_fields()
        
        # ========== SEÇÃO 4: LINHAS ALUGADAS ==========
        self._configure_linhas_fields()
    
    def _configure_estacoes_moveis_fields(self):
        """Configuração para campos de estações móveis"""
        # Campos de valores grandes (pré-pagos em milhões)
        large_number_fields = [
            'afectos_planos_pre_pagos',
            'afectos_planos_pre_pagos_utilizacao'
        ]
        
        for field_name in large_number_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number',
                    'title': 'Valores em milhões'
                })
        
        # Campos normais
        normal_fields = [
            'afectos_planos_pos_pagos',
            'afectos_planos_pos_pagos_utilizacao',
            'associados_situacoes_especificas',
            'outros_residuais'
        ]
        
        for field_name in normal_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0'
                })
    
    def _configure_servicos_fields(self):
        """Configuração para campos de serviços"""
        # SMS e Roaming (valores grandes)
        large_service_fields = [
            'sms',
            'roaming_internacional_out_parc_roaming_out',
            'utilizadores_servico_3g_upgrades',
            'utilizadores_servico_4g'
        ]
        
        for field_name in large_service_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number'
                })
        
        # Campos opcionais (podem ser NA)
        optional_fields = ['mms', 'mobile_tv']
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
                self.fields[field_name].widget.attrs.update({
                    'placeholder': 'NA ou valor',
                    'min': '0'
                })
        
        # Campos de internet e placas
        internet_fields = [
            'utilizadores_acesso_internet_3g',
            'utilizadores_3g_placas_box',
            'utilizadores_3g_placas_usb',
            'utilizadores_acesso_internet_4g',
            'utilizadores_4g_placas_box',
            'utilizadores_4g_placas_usb'
        ]
        
        for field_name in internet_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0'
                })
    
    def _configure_mobile_money_fields(self):
        """Configuração para campos de Mobile Money"""
        # Campos de utilizadores (valores grandes)
        user_fields = [
            'numero_utilizadores',
            'numero_utilizadores_mulher',
            'numero_utilizadores_homem'
        ]
        
        for field_name in user_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number'
                })
        
        # Campos monetários (valores em bilhões)
        money_fields = [
            'total_carregamentos', 'total_carregamentos_mulher', 'total_carregamentos_homem',
            'total_levantamentos', 'total_levantamentos_mulher', 'total_levantamentos_homem',
            'total_transferencias', 'total_transferencias_mulher', 'total_transferencias_homem'
        ]
        
        for field_name in money_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.TextInput(attrs={
                    'class': 'form-control form-control-questionario',
                    'placeholder': '0.00',
                    'data-format': 'currency',
                    'data-decimals': '2',
                    'pattern': r'^\d+(\.\d{1,2})?$',
                    'title': 'Valor monetário (suporta bilhões)'
                })
    
    def _configure_linhas_fields(self):
        """Configuração para campos de linhas alugadas"""
        linhas_fields = [
            'linhas_64kbit', 'linhas_128kbit', 'linhas_256kbit',
            'linhas_512kbit', 'linhas_1mbit', 'linhas_maior_2mbit'
        ]
        
        for field_name in linhas_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'title': 'Número de linhas alugadas'
                })
    
    def clean(self):
        """Validação completa do formulário"""
        cleaned_data = super().clean()
        errors = []
        
        # ========== VALIDAÇÕES DE ESTAÇÕES MÓVEIS ==========
        self._validate_estacoes_moveis(cleaned_data, errors)
        
        # ========== VALIDAÇÕES DE BANDA LARGA ==========
        self._validate_banda_larga(cleaned_data, errors)
        
        # ========== VALIDAÇÕES DE MOBILE MONEY ==========
        self._validate_mobile_money(cleaned_data, errors)
        
        # Lançar erros se houver
        if errors:
            raise ValidationError(errors)
        
        return cleaned_data
    
    def _validate_estacoes_moveis(self, data, errors):
        """Valida dados de estações móveis"""
        # Validar utilização não excede total (pós-pagos)
        pos_pagos = data.get('afectos_planos_pos_pagos', 0) or 0
        pos_pagos_util = data.get('afectos_planos_pos_pagos_utilizacao', 0) or 0
        
        if pos_pagos_util > pos_pagos:
            errors.append(ValidationError(
                'Utilização de pós-pagos (%(util)s) não pode exceder total (%(total)s)',
                code='invalid_pos_pagos',
                params={'util': pos_pagos_util, 'total': pos_pagos}
            ))
        
        # Validar utilização não excede total (pré-pagos)
        pre_pagos = data.get('afectos_planos_pre_pagos', 0) or 0
        pre_pagos_util = data.get('afectos_planos_pre_pagos_utilizacao', 0) or 0
        
        if pre_pagos_util > pre_pagos:
            errors.append(ValidationError(
                'Utilização de pré-pagos (%(util)s) não pode exceder total (%(total)s)',
                code='invalid_pre_pagos',
                params={'util': pre_pagos_util, 'total': pre_pagos}
            ))
    
    def _validate_banda_larga(self, data, errors):
        """Valida dados de banda larga 3G/4G"""
        # Validar placas 3G
        acesso_3g = data.get('utilizadores_acesso_internet_3g', 0) or 0
        placas_box_3g = data.get('utilizadores_3g_placas_box', 0) or 0
        placas_usb_3g = data.get('utilizadores_3g_placas_usb', 0) or 0
        
        if acesso_3g > 0 and (placas_box_3g + placas_usb_3g) > acesso_3g:
            errors.append(ValidationError(
                'Total de placas 3G (%(placas)s) não pode exceder utilizadores de internet 3G (%(internet)s)',
                code='invalid_3g_placas',
                params={'placas': placas_box_3g + placas_usb_3g, 'internet': acesso_3g}
            ))
        
        # Validar placas 4G
        acesso_4g = data.get('utilizadores_acesso_internet_4g', 0) or 0
        placas_box_4g = data.get('utilizadores_4g_placas_box', 0) or 0
        placas_usb_4g = data.get('utilizadores_4g_placas_usb', 0) or 0
        
        if acesso_4g > 0 and (placas_box_4g + placas_usb_4g) > acesso_4g:
            errors.append(ValidationError(
                'Total de placas 4G (%(placas)s) não pode exceder utilizadores de internet 4G (%(internet)s)',
                code='invalid_4g_placas',
                params={'placas': placas_box_4g + placas_usb_4g, 'internet': acesso_4g}
            ))
    
    def _validate_mobile_money(self, data, errors):
        """Valida dados de Mobile Money"""
        # Validar utilizadores por gênero
        total_users = data.get('numero_utilizadores', 0) or 0
        users_mulher = data.get('numero_utilizadores_mulher', 0) or 0
        users_homem = data.get('numero_utilizadores_homem', 0) or 0
        
        if (users_mulher + users_homem) > total_users:
            errors.append(ValidationError(
                'Soma de utilizadores por gênero (%(soma)s) excede total (%(total)s)',
                code='invalid_users_gender',
                params={'soma': users_mulher + users_homem, 'total': total_users}
            ))
        
        # Validar carregamentos
        total_carr = data.get('total_carregamentos', Decimal('0')) or Decimal('0')
        carr_mulher = data.get('total_carregamentos_mulher', Decimal('0')) or Decimal('0')
        carr_homem = data.get('total_carregamentos_homem', Decimal('0')) or Decimal('0')
        
        if abs((carr_mulher + carr_homem) - total_carr) > Decimal('0.01'):
            errors.append(ValidationError(
                'Soma de carregamentos por gênero não coincide com total',
                code='invalid_carregamentos'
            ))
        
        # Validar levantamentos
        total_lev = data.get('total_levantamentos', Decimal('0')) or Decimal('0')
        lev_mulher = data.get('total_levantamentos_mulher', Decimal('0')) or Decimal('0')
        lev_homem = data.get('total_levantamentos_homem', Decimal('0')) or Decimal('0')
        
        if abs((lev_mulher + lev_homem) - total_lev) > Decimal('0.01'):
            errors.append(ValidationError(
                'Soma de levantamentos por gênero não coincide com total',
                code='invalid_levantamentos'
            ))
        
        # Validar transferências
        total_trans = data.get('total_transferencias', Decimal('0')) or Decimal('0')
        trans_mulher = data.get('total_transferencias_mulher', Decimal('0')) or Decimal('0')
        trans_homem = data.get('total_transferencias_homem', Decimal('0')) or Decimal('0')
        
        if abs((trans_mulher + trans_homem) - total_trans) > Decimal('0.01'):
            errors.append(ValidationError(
                'Soma de transferências por gênero não coincide com total',
                code='invalid_transferencias'
            ))
    
    def clean_total_carregamentos(self):
        """Limpa e valida valores monetários de carregamentos"""
        value = self.cleaned_data.get('total_carregamentos')
        if value and value > Decimal('999999999999.99'):  # Trilhões
            raise ValidationError('Valor excede o limite máximo permitido')
        return value
    
    def clean_total_levantamentos(self):
        """Limpa e valida valores monetários de levantamentos"""
        value = self.cleaned_data.get('total_levantamentos')
        if value and value > Decimal('999999999999.99'):  # Trilhões
            raise ValidationError('Valor excede o limite máximo permitido')
        return value
    
    def clean_total_transferencias(self):
        """Limpa e valida valores monetários de transferências"""
        value = self.cleaned_data.get('total_transferencias')
        if value and value > Decimal('999999999999.99'):  # Trilhões
            raise ValidationError('Valor excede o limite máximo permitido')
        return value