from django import forms
from ..models import InvestimentoIndicador

class InvestimentoForm(forms.ModelForm):
    # Campo dinâmico para outros investimentos
    novo_campo_nome = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do novo investimento'
        })
    )
    novo_campo_valor = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Valor'
        })
    )

    class Meta:
        model = InvestimentoIndicador
        fields = '__all__'  # Pega todos os campos do modelo
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao', 'outros_investimentos']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar classes Bootstrap para todos os campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Se existem outros investimentos, criar campos para eles
        if self.instance.pk and self.instance.outros_investimentos:
            for nome, valor in self.instance.outros_investimentos.items():
                field_name = f'outro_investimento_{nome}'
                self.fields[field_name] = forms.DecimalField(
                    initial=valor,
                    required=False,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Processar campos dinâmicos
        outros_investimentos = {}
        
        # Manter investimentos existentes
        if instance.outros_investimentos:
            outros_investimentos.update(instance.outros_investimentos)

        # Adicionar novo investimento se fornecido
        novo_nome = self.cleaned_data.get('novo_campo_nome')
        novo_valor = self.cleaned_data.get('novo_campo_valor')
        if novo_nome and novo_valor:
            outros_investimentos[novo_nome] = str(novo_valor)

        # Atualizar valores de investimentos existentes
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('outro_investimento_') and value:
                nome = field_name.replace('outro_investimento_', '')
                outros_investimentos[nome] = str(value)

        instance.outros_investimentos = outros_investimentos

        if commit:
            instance.save()
        return instance