from django import forms
from ..models import AssinantesIndicador

class AssinantesIndicadorForm(forms.ModelForm):
    class Meta:
        model = AssinantesIndicador
        fields = [
            'operadora', 'ano', 'mes',
            'assinantes_pre_pago', 'assinantes_pos_pago',
            'assinantes_fixo',
            'assinantes_internet_movel', 'assinantes_internet_fixa',
        ]
        widgets = {
            'operadora': forms.Select(attrs={'class': 'form-select'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'mes': forms.Select(attrs={'class': 'form-select'}, choices=[(i, i) for i in range(1, 13)]),
            'assinantes_pre_pago': forms.NumberInput(attrs={'class': 'form-control'}),
            'assinantes_pos_pago': forms.NumberInput(attrs={'class': 'form-control'}),
            'assinantes_fixo': forms.NumberInput(attrs={'class': 'form-control'}),
            'assinantes_internet_movel': forms.NumberInput(attrs={'class': 'form-control'}),
            'assinantes_internet_fixa': forms.NumberInput(attrs={'class': 'form-control'}),
        } 