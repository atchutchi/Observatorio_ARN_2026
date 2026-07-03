from django import forms
from ..models import TarifarioVozTelecelIndicador

class TarifarioVozTelecelForm(forms.ModelForm):
    class Meta:
        model = TarifarioVozTelecelIndicador
        # Exclude operadora (set automatically) and metadata fields
        exclude = ['operadora', 'criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']
        
        widgets = {
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'mes': forms.Select(attrs={'class': 'form-select'}, choices=[(i, i) for i in range(1, 13)]),
            # Add widgets for all other DecimalFields to use number input
            'huawei_4g_lte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'huawei_mobile_wifi_4g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_30mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_100mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_300mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_1gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_650mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_1000mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_1_5gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_10gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_18gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_30gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_50gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_60gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_120gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_yello_350mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_yello_1_5gb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_yello_1_5gb_7dias': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_1hora': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_3horas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pacote_9horas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_imposto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'link_plano': forms.URLInput(attrs={'class': 'form-control'}),
        } 