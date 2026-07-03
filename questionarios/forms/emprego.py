from django import forms
from ..models.emprego import EmpregoIndicador

class EmpregoForm(forms.ModelForm):
    class Meta:
        model = EmpregoIndicador
        fields = '__all__'
        exclude = ['criado_por', 'atualizado_por', 'data_criacao', 'data_atualizacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select)):
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        nacionais_total = cleaned_data.get('nacionais_total')
        homens = cleaned_data.get('nacionais_homem')
        mulheres = cleaned_data.get('nacionais_mulher')

        if nacionais_total and homens and mulheres:
            if homens + mulheres != nacionais_total:
                raise forms.ValidationError(
                    'A soma de homens e mulheres deve ser igual ao total de nacionais'
                )
        return cleaned_data