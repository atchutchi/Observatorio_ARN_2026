from django import forms
from django.core.exceptions import ValidationError
from .models.estacoes_moveis import EstacoesMoveisIndicador
from .models.trafego_originado import TrafegoOriginadoIndicador

class EstacoesMoveisForm(forms.ModelForm):
    """Formulário para o modelo EstacoesMoveisIndicador."""
    
    class Meta:
        model = EstacoesMoveisIndicador
        fields = '__all__'
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

# ... outros formulários existentes ... 