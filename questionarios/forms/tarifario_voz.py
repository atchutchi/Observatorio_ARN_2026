from django import forms
from ..models.tarifario_voz import TarifarioVozOrangeIndicador, TarifarioVozMTNIndicador

class TarifarioVozOrangeForm(forms.ModelForm):
    class Meta:
        model = TarifarioVozOrangeIndicador
        fields = '__all__'  # Pega todos os campos do modelo
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe form-control para todos os campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.URLInput, forms.Select)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 3

    def clean(self):
        cleaned_data = super().clean()
        # Adicione validações personalizadas aqui se necessário
        return cleaned_data


class TarifarioVozMTNForm(forms.ModelForm):
    class Meta:
        model = TarifarioVozMTNIndicador
        fields = '__all__'  # Pega todos os campos do modelo
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe form-control para todos os campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.URLInput, forms.Select)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 3

    def clean(self):
        cleaned_data = super().clean()
        # Adicione validações personalizadas aqui se necessário
        return cleaned_data