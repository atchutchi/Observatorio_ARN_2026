from django import forms
from django.utils import timezone
from ..models.base import IndicadorBase

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Selecione o arquivo Excel (.xlsx)',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'}),
        help_text='Certifique-se que o arquivo segue a estrutura esperada.'
    )
    
    # Dropdown for operadora selection
    operadora = forms.ChoiceField(
        label='Operadora',
        choices=IndicadorBase.OPERADORAS_CHOICES,
        required=True,
        help_text='Selecione a operadora para este conjunto de dados.'
    )
    
    # Year for the data
    ano = forms.IntegerField(
        label='Ano',
        initial=timezone.now().year,
        min_value=2000,
        max_value=2100,
        required=True,
        help_text='Ano dos dados (substitui qualquer ano detectado no arquivo).'
    )
    # We can add fields later to specify year/operadora if not in the file
    # ano = forms.IntegerField(label='Ano dos Dados') 
    # operadora = forms.ChoiceField(label='Operadora', choices=...) 