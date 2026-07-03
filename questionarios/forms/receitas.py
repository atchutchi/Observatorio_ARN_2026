# forms/receitas.py
from django import forms
from ..models.receitas import ReceitasIndicador

class ReceitasForm(forms.ModelForm):
    class Meta:
        model = ReceitasIndicador
        fields = '__all__'
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select)):
                field.widget.attrs['class'] = 'form-control'