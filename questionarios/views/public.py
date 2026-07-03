"""
Views públicas para visualização de dados sem necessidade de autenticação
"""
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.db.models import Sum, Avg
from django.utils import timezone

from ..models import (
    EstacoesMoveisIndicador,
    TrafegoOriginadoIndicador,
    TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador,
    LBIIndicador,
    TrafegoInternetIndicador,
    InternetFixoIndicador,
    ReceitasIndicador,
    EmpregoIndicador,
    InvestimentoIndicador
)

class PublicIndexView(TemplateView):
    """
    View pública para a página inicial com resumos dos dados
    """
    template_name = 'questionarios/public/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = timezone.now().year
        
        # Estatísticas gerais
        context['estacoes_moveis_count'] = EstacoesMoveisIndicador.objects.filter(ano=current_year).aggregate(total=Sum('numero_utilizadores'))['total'] or 0
        context['internet_fixo_count'] = InternetFixoIndicador.objects.filter(ano=current_year).aggregate(total=Sum('cidade_bissau'))['total'] or 0
        context['emprego_count'] = EmpregoIndicador.objects.filter(ano=current_year).aggregate(total=Sum('emprego_direto_total'))['total'] or 0
        
        # Anos disponíveis para seleção
        anos_disponiveis = set()
        for model in [EstacoesMoveisIndicador, TrafegoOriginadoIndicador, EmpregoIndicador]:
            anos = model.objects.values_list('ano', flat=True).distinct()
            anos_disponiveis.update(anos)
        
        context['anos_disponiveis'] = sorted(anos_disponiveis, reverse=True)
        context['operadoras'] = [choice[0] for choice in EstacoesMoveisIndicador.OPERADORA_CHOICES]
        
        return context

class PublicEstacoesMoveisListView(ListView):
    """
    View pública para listar dados de estações móveis
    """
    model = EstacoesMoveisIndicador
    template_name = 'questionarios/public/estacoes_moveis_list.html'
    context_object_name = 'estacoes_moveis_list'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ano = self.request.GET.get('ano', timezone.now().year)
        operadora = self.request.GET.get('operadora')
        
        queryset = queryset.filter(ano=ano)
        if operadora:
            queryset = queryset.filter(operadora=operadora)
            
        return queryset.order_by('-ano', '-mes', 'operadora')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anos_disponiveis'] = self.model.objects.values_list('ano', flat=True).distinct().order_by('-ano')
        context['operadoras'] = [choice[0] for choice in self.model.OPERADORA_CHOICES]
        context['ano_selecionado'] = self.request.GET.get('ano', timezone.now().year)
        context['operadora_selecionada'] = self.request.GET.get('operadora', '')
        
        return context

class PublicEmpregoListView(ListView):
    """
    View pública para listar dados de emprego
    """
    model = EmpregoIndicador
    template_name = 'questionarios/public/emprego_list.html'
    context_object_name = 'emprego_list'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ano = self.request.GET.get('ano', timezone.now().year)
        operadora = self.request.GET.get('operadora')
        
        queryset = queryset.filter(ano=ano)
        if operadora:
            queryset = queryset.filter(operadora=operadora)
            
        return queryset.order_by('-ano', '-mes', 'operadora')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anos_disponiveis'] = self.model.objects.values_list('ano', flat=True).distinct().order_by('-ano')
        context['operadoras'] = [choice[0] for choice in self.model.OPERADORA_CHOICES]
        context['ano_selecionado'] = self.request.GET.get('ano', timezone.now().year)
        context['operadora_selecionada'] = self.request.GET.get('operadora', '')
        
        # Totais por operadora
        if context['emprego_list']:
            por_operadora = {}
            for op in self.model.OPERADORA_CHOICES:
                dados_op = [e for e in context['emprego_list'] if e.operadora == op[0]]
                if dados_op:
                    por_operadora[op[1]] = {
                        'direto': sum(e.emprego_direto_total for e in dados_op) / len(dados_op),
                        'nacionais': sum(e.nacionais_total for e in dados_op) / len(dados_op),
                        'indireto': sum(e.emprego_indireto for e in dados_op) / len(dados_op),
                        'total': sum(e.calcular_total_geral() for e in dados_op) / len(dados_op),
                    }
            context['por_operadora'] = por_operadora
            
        return context

class PublicInternetFixoListView(ListView):
    """
    View pública para listar dados de internet fixo
    """
    model = InternetFixoIndicador
    template_name = 'questionarios/public/internet_fixo_list.html'
    context_object_name = 'internet_fixo_list'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ano = self.request.GET.get('ano', timezone.now().year)
        operadora = self.request.GET.get('operadora')
        
        queryset = queryset.filter(ano=ano)
        if operadora:
            queryset = queryset.filter(operadora=operadora)
            
        return queryset.order_by('-ano', '-mes', 'operadora')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anos_disponiveis'] = self.model.objects.values_list('ano', flat=True).distinct().order_by('-ano')
        context['operadoras'] = [choice[0] for choice in self.model.OPERADORA_CHOICES]
        context['ano_selecionado'] = self.request.GET.get('ano', timezone.now().year)
        context['operadora_selecionada'] = self.request.GET.get('operadora', '')
        
        # Calcular totais por região
        regioes = ['cidade_bissau', 'bafata', 'biombo', 'bolama_bijagos', 'cacheu', 'gabu', 'oio', 'quinara', 'tombali']
        totais_regioes = {}
        
        for regiao in regioes:
            total = sum(getattr(item, regiao, 0) or 0 for item in context['internet_fixo_list'])
            totais_regioes[regiao] = total
            
        context['totais_regioes'] = totais_regioes
        
        return context


# ===== NOVA VIEW DE GESTÃO DE DADOS =====

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class DataManagementView(TemplateView):
    """
    View principal da gestão de dados - lista todos os indicadores
    """
    template_name = 'questionarios/data_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Central de Gestão de Dados'
        context['current_year'] = timezone.now().year
        
        return context

# Function-based view para compatibilidade com urls.py
@login_required
def data_management_view(request):
    """View principal da gestão de dados - lista todos os indicadores"""
    context = {
        'title': 'Central de Gestão de Dados',
        'current_year': timezone.now().year
    }
    return render(request, 'questionarios/data_management.html', context) 