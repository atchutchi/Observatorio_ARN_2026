"""
Formulário para Tráfego Originado baseado na estrutura KPI ARN.
"""

from django import forms
from django.core.exceptions import ValidationError
from ..models.trafego_originado import TrafegoOriginadoIndicador

class TrafegoOriginadoForm(forms.ModelForm):
    """
    Formulário para indicadores de Tráfego Originado (Seção 5 KPI ARN).
    """
    
    class Meta:
        model = TrafegoOriginadoIndicador
        fields = [
            # Dados básicos
            'ano', 'mes', 'operadora',
            
            # SEÇÃO 5.1: TRÁFEGO DE DADOS
            # 5.1.1 - 2G
            'trafego_dados_2g_mbytes', 'trafego_dados_2g_sessoes',
            
            # 5.1.2 - 3G
            'trafego_dados_3g_upgrade_mbytes', 'internet_3g_mbytes',
            'internet_3g_placas_modem_mbytes', 'internet_3g_modem_usb_mbytes',
            'trafego_dados_3g_upgrade_sessoes', 'internet_3g_sessoes',
            'internet_3g_placas_modem_sessoes', 'internet_3g_modem_usb_sessoes',
            
            # 5.1.3 - 4G
            'trafego_dados_4g_mbytes', 'internet_4g_mbytes',
            'internet_4g_placas_modem_mbytes', 'internet_4g_modem_usb_mbytes',
            'trafego_dados_4g_sessoes', 'internet_4g_sessoes',
            'internet_4g_placas_modem_sessoes', 'internet_4g_modem_usb_sessoes',
            
            # SEÇÃO 5.2: TRÁFEGO DE MENSAGENS (SMS)
            'sms_total', 'sms_on_net', 'sms_off_net_nacional',
            'sms_internacional_total', 'sms_cedeao', 'sms_palop',
            'sms_cplp', 'sms_resto_africa', 'sms_resto_mundo',
            
            # SEÇÃO 5.3: VOLUME DE TRÁFEGO DE VOZ (MINUTOS)
            'voz_total_minutos', 'voz_on_net_minutos', 'voz_off_net_nacional_minutos',
            'voz_rede_fixa_minutos', 'voz_outras_redes_moveis_minutos',
            'voz_internacional_total_minutos', 'voz_cedeao_minutos', 'voz_palop_minutos',
            'voz_cplp_minutos', 'voz_resto_africa_minutos', 'voz_resto_mundo_minutos',
            
            # SEÇÃO 5.4: NÚMERO DE COMUNICAÇÕES DE VOZ (CHAMADAS)
            'chamadas_total', 'chamadas_on_net', 'chamadas_off_net_nacional',
            'chamadas_rede_fixa', 'chamadas_outras_redes_moveis',
            'chamadas_internacional_total', 'chamadas_cedeao', 'chamadas_palop',
            'chamadas_cplp', 'chamadas_resto_africa', 'chamadas_resto_mundo',
            
            # SEÇÃO 5.5: OUTROS SERVIÇOS
            'numeros_curtos', 'mms_total'
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
        
        # Adicionar classe form-control a todos os campos
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control-questionario'
            else:
                field.widget.attrs['class'] = 'form-control form-control-questionario'
        
        # Configurar campos específicos
        self._configure_data_fields()
        self._configure_sms_fields()
        self._configure_voice_fields()
        self._configure_calls_fields()
        self._configure_other_fields()
    
    def _configure_data_fields(self):
        """Configura campos de tráfego de dados"""
        # Campos de volume (MBytes) - valores grandes
        volume_fields = [
            'trafego_dados_2g_mbytes',
            'trafego_dados_3g_upgrade_mbytes', 'internet_3g_mbytes',
            'internet_3g_placas_modem_mbytes', 'internet_3g_modem_usb_mbytes',
            'trafego_dados_4g_mbytes', 'internet_4g_mbytes',
            'internet_4g_placas_modem_mbytes', 'internet_4g_modem_usb_mbytes'
        ]
        
        for field_name in volume_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number',
                    'title': 'Volume em MBytes'
                })
        
        # Campos de sessões
        session_fields = [
            'trafego_dados_2g_sessoes',
            'trafego_dados_3g_upgrade_sessoes', 'internet_3g_sessoes',
            'internet_3g_placas_modem_sessoes', 'internet_3g_modem_usb_sessoes',
            'trafego_dados_4g_sessoes', 'internet_4g_sessoes',
            'internet_4g_placas_modem_sessoes', 'internet_4g_modem_usb_sessoes'
        ]
        
        for field_name in session_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number',
                    'title': 'Número de sessões'
                })
    
    def _configure_sms_fields(self):
        """Configura campos de SMS"""
        sms_fields = [
            'sms_total', 'sms_on_net', 'sms_off_net_nacional',
            'sms_internacional_total', 'sms_cedeao', 'sms_palop',
            'sms_cplp', 'sms_resto_africa', 'sms_resto_mundo'
        ]
        
        for field_name in sms_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number',
                    'title': 'Número de mensagens SMS'
                })
        
        # Campos totais são readonly (calculados)
        if 'sms_total' in self.fields:
            self.fields['sms_total'].widget.attrs['data-calculated'] = 'true'
        if 'sms_internacional_total' in self.fields:
            self.fields['sms_internacional_total'].widget.attrs['data-calculated'] = 'true'
    
    def _configure_voice_fields(self):
        """Configura campos de voz (minutos)"""
        voice_fields = [
            'voz_total_minutos', 'voz_on_net_minutos', 'voz_off_net_nacional_minutos',
            'voz_rede_fixa_minutos', 'voz_outras_redes_moveis_minutos',
            'voz_internacional_total_minutos', 'voz_cedeao_minutos', 'voz_palop_minutos',
            'voz_cplp_minutos', 'voz_resto_africa_minutos', 'voz_resto_mundo_minutos'
        ]
        
        for field_name in voice_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number',
                    'title': 'Volume em minutos'
                })
        
        # Campos totais são readonly (calculados)
        if 'voz_total_minutos' in self.fields:
            self.fields['voz_total_minutos'].widget.attrs['data-calculated'] = 'true'
        if 'voz_internacional_total_minutos' in self.fields:
            self.fields['voz_internacional_total_minutos'].widget.attrs['data-calculated'] = 'true'
    
    def _configure_calls_fields(self):
        """Configura campos de chamadas"""
        calls_fields = [
            'chamadas_total', 'chamadas_on_net', 'chamadas_off_net_nacional',
            'chamadas_rede_fixa', 'chamadas_outras_redes_moveis',
            'chamadas_internacional_total', 'chamadas_cedeao', 'chamadas_palop',
            'chamadas_cplp', 'chamadas_resto_africa', 'chamadas_resto_mundo'
        ]
        
        for field_name in calls_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0',
                    'min': '0',
                    'data-format': 'large-number',
                    'title': 'Número de chamadas'
                })
        
        # Campos totais são readonly (calculados)
        if 'chamadas_total' in self.fields:
            self.fields['chamadas_total'].widget.attrs['data-calculated'] = 'true'
        if 'chamadas_internacional_total' in self.fields:
            self.fields['chamadas_internacional_total'].widget.attrs['data-calculated'] = 'true'
    
    def _configure_other_fields(self):
        """Configura outros campos"""
        other_fields = ['numeros_curtos', 'mms_total']
        
        for field_name in other_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
                self.fields[field_name].widget.attrs.update({
                    'placeholder': '0 ou NA',
                    'min': '0',
                    'title': 'Opcional - deixe vazio se não aplicável'
                })
    
    def clean(self):
        """Validação completa do formulário"""
        cleaned_data = super().clean()
        errors = []
        
        # Validar totais de SMS
        self._validate_sms_totals(cleaned_data, errors)
        
        # Validar totais de voz
        self._validate_voice_totals(cleaned_data, errors)
        
        # Validar totais de chamadas
        self._validate_calls_totals(cleaned_data, errors)
        
        # Validar coerência entre minutos e chamadas
        self._validate_coherence(cleaned_data, errors)
        
        if errors:
            raise ValidationError(errors)
        
        return cleaned_data
    
    def _validate_sms_totals(self, data, errors):
        """Valida totais de SMS"""
        # Calcular total nacional
        sms_nacional = (
            (data.get('sms_on_net') or 0) +
            (data.get('sms_off_net_nacional') or 0)
        )
        
        # Calcular total internacional
        sms_internacional = (
            (data.get('sms_cedeao') or 0) +
            (data.get('sms_palop') or 0) +
            (data.get('sms_cplp') or 0) +
            (data.get('sms_resto_africa') or 0) +
            (data.get('sms_resto_mundo') or 0)
        )
        
        # Validar total internacional
        if data.get('sms_internacional_total'):
            if sms_internacional != data['sms_internacional_total']:
                errors.append(ValidationError(
                    'Total SMS internacional (%(total)s) não coincide com soma das regiões (%(soma)s)',
                    code='invalid_sms_internacional',
                    params={'total': data['sms_internacional_total'], 'soma': sms_internacional}
                ))
        else:
            data['sms_internacional_total'] = sms_internacional
        
        # Validar total geral
        sms_total_calculado = sms_nacional + sms_internacional
        if data.get('sms_total'):
            if sms_total_calculado != data['sms_total']:
                errors.append(ValidationError(
                    'Total SMS (%(total)s) não coincide com soma (%(soma)s)',
                    code='invalid_sms_total',
                    params={'total': data['sms_total'], 'soma': sms_total_calculado}
                ))
        else:
            data['sms_total'] = sms_total_calculado
    
    def _validate_voice_totals(self, data, errors):
        """Valida totais de voz"""
        # Calcular total nacional
        voz_nacional = (
            (data.get('voz_on_net_minutos') or 0) +
            (data.get('voz_off_net_nacional_minutos') or 0) +
            (data.get('voz_rede_fixa_minutos') or 0) +
            (data.get('voz_outras_redes_moveis_minutos') or 0)
        )
        
        # Calcular total internacional
        voz_internacional = (
            (data.get('voz_cedeao_minutos') or 0) +
            (data.get('voz_palop_minutos') or 0) +
            (data.get('voz_cplp_minutos') or 0) +
            (data.get('voz_resto_africa_minutos') or 0) +
            (data.get('voz_resto_mundo_minutos') or 0)
        )
        
        # Validar total internacional
        if data.get('voz_internacional_total_minutos'):
            if voz_internacional != data['voz_internacional_total_minutos']:
                errors.append(ValidationError(
                    'Total voz internacional não coincide com soma das regiões',
                    code='invalid_voz_internacional'
                ))
        else:
            data['voz_internacional_total_minutos'] = voz_internacional
        
        # Validar total geral
        voz_total_calculado = voz_nacional + voz_internacional
        if data.get('voz_total_minutos'):
            if voz_total_calculado != data['voz_total_minutos']:
                errors.append(ValidationError(
                    'Total voz não coincide com soma dos componentes',
                    code='invalid_voz_total'
                ))
        else:
            data['voz_total_minutos'] = voz_total_calculado
    
    def _validate_calls_totals(self, data, errors):
        """Valida totais de chamadas"""
        # Calcular total nacional
        chamadas_nacional = (
            (data.get('chamadas_on_net') or 0) +
            (data.get('chamadas_off_net_nacional') or 0) +
            (data.get('chamadas_rede_fixa') or 0) +
            (data.get('chamadas_outras_redes_moveis') or 0)
        )
        
        # Calcular total internacional
        chamadas_internacional = (
            (data.get('chamadas_cedeao') or 0) +
            (data.get('chamadas_palop') or 0) +
            (data.get('chamadas_cplp') or 0) +
            (data.get('chamadas_resto_africa') or 0) +
            (data.get('chamadas_resto_mundo') or 0)
        )
        
        # Validar total internacional
        if data.get('chamadas_internacional_total'):
            if chamadas_internacional != data['chamadas_internacional_total']:
                errors.append(ValidationError(
                    'Total chamadas internacional não coincide com soma das regiões',
                    code='invalid_chamadas_internacional'
                ))
        else:
            data['chamadas_internacional_total'] = chamadas_internacional
        
        # Validar total geral
        chamadas_total_calculado = chamadas_nacional + chamadas_internacional
        if data.get('chamadas_total'):
            if chamadas_total_calculado != data['chamadas_total']:
                errors.append(ValidationError(
                    'Total chamadas não coincide com soma dos componentes',
                    code='invalid_chamadas_total'
                ))
        else:
            data['chamadas_total'] = chamadas_total_calculado
    
    def _validate_coherence(self, data, errors):
        """Valida coerência entre dados relacionados"""
        # Verificar se há chamadas sem minutos
        if data.get('chamadas_total', 0) > 0 and data.get('voz_total_minutos', 0) == 0:
            errors.append(ValidationError(
                'Existem chamadas registradas mas nenhum minuto de voz',
                code='incoherent_calls_minutes'
            ))
        
        # Verificar duração média das chamadas (não deve ser muito alta)
        if data.get('chamadas_total', 0) > 0:
            duracao_media = data.get('voz_total_minutos', 0) / data['chamadas_total']
            if duracao_media > 60:  # Mais de 60 minutos por chamada é suspeito
                errors.append(ValidationError(
                    f'Duração média das chamadas ({duracao_media:.1f} min) parece muito alta',
                    code='suspicious_call_duration'
                ))