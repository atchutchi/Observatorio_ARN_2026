from django import forms
from ..models.trafego_roaming_internacional import TrafegoRoamingInternacionalIndicador

class TrafegoRoamingInternacionalForm(forms.ModelForm):
    class Meta:
        model = TrafegoRoamingInternacionalIndicador
        fields = '__all__'
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe form-control para todos os campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select)):
                field.widget.attrs['class'] = 'form-control'