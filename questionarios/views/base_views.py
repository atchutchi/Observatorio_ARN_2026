"""
Views base genéricas para eliminar duplicação de código nos indicadores.
Todas as apps seguem o mesmo padrão CRUD.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from abc import ABC, abstractmethod

# Constantes para choices
MONTH_CHOICES = [
    (1, 'Janeiro'),
    (2, 'Fevereiro'),
    (3, 'Março'),
    (4, 'Abril'),
    (5, 'Maio'),
    (6, 'Junho'),
    (7, 'Julho'),
    (8, 'Agosto'),
    (9, 'Setembro'),
    (10, 'Outubro'),
    (11, 'Novembro'),
    (12, 'Dezembro'),
]

OPERADORAS_CHOICES = [
    ('orange', 'Orange'),
    ('telecel', 'TELECEL'),
    ('telecel', 'TELECEL'),
]


class BaseIndicadorMixin(ABC):
    """Mixin base que define as propriedades que cada view deve implementar."""
    
    @property
    @abstractmethod
    def model(self):
        """Modelo do indicador."""
        pass
    
    @property
    @abstractmethod
    def form_class(self):
        """Classe do formulário."""
        pass
    
    @property
    @abstractmethod
    def template_prefix(self):
        """Prefixo dos templates (ex: 'estacoes_moveis')."""
        pass
    
    @property
    @abstractmethod
    def url_namespace(self):
        """Namespace da URL (ex: 'estacoes_moveis')."""
        pass
    
    @property
    @abstractmethod
    def permission_base(self):
        """Base da permissão (ex: 'estacoesmoveisindicador')."""
        pass


class BaseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView, BaseIndicadorMixin):
    """View base para criação de indicadores."""
    
    def get_template_names(self):
        return [f'questionarios/{self.template_prefix}_form.html']
    
    def get_success_url(self):
        return reverse_lazy(f'questionarios:{self.url_namespace}_list')
    
    def get_permission_required(self):
        return f'questionarios.add_{self.permission_base}'
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, 'Registro criado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar registro. Verifique os dados.')
        return super().form_invalid(form)


class FilteredListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Base ListView with filtering capabilities and month choices."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        operadora = self.request.GET.get('operadora')
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')
        
        if operadora:
            queryset = queryset.filter(operadora=operadora)
        if ano:
            try:
                queryset = queryset.filter(ano=int(ano))
            except ValueError:
                pass # Ignore invalid year input
        if mes:
            try:
                queryset = queryset.filter(mes=int(mes))
            except ValueError:
                pass # Ignore invalid month input
        
        return queryset.order_by('-ano', '-mes') # Default ordering
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mes_choices'] = MONTH_CHOICES
        context['operadoras_choices'] = OPERADORAS_CHOICES
        
        # Anos disponíveis (últimos 10 anos)
        from datetime import datetime
        current_year = datetime.now().year
        context['anos_choices'] = [(year, year) for year in range(current_year - 10, current_year + 2)]
        
        # Valores selecionados nos filtros
        context['operadora_selecionada'] = self.request.GET.get('operadora', '')
        context['ano_selecionado'] = self.request.GET.get('ano', '')
        context['mes_selecionado'] = self.request.GET.get('mes', '')
        
        return context


class BaseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, BaseIndicadorMixin):
    """View base para atualização de indicadores."""
    
    def get_template_names(self):
        return [f'questionarios/{self.template_prefix}_form.html']
    
    def get_success_url(self):
        return reverse_lazy(f'questionarios:{self.url_namespace}_list')
    
    def get_permission_required(self):
        return f'questionarios.change_{self.permission_base}'
    
    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        messages.success(self.request, 'Registro atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar registro. Verifique os dados.')
        return super().form_invalid(form)


class BaseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView, BaseIndicadorMixin):
    """View base para exclusão de indicadores."""
    
    def get_template_names(self):
        return [f'questionarios/{self.template_prefix}_confirm_delete.html']
    
    def get_success_url(self):
        return reverse_lazy(f'questionarios:{self.url_namespace}_list')
    
    def get_permission_required(self):
        return f'questionarios.delete_{self.permission_base}'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Registro excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


class BaseDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView, BaseIndicadorMixin):
    """View base para detalhes de indicadores."""
    
    context_object_name = 'indicador'
    
    def get_template_names(self):
        return [f'questionarios/{self.template_prefix}_detail.html']
    
    def get_permission_required(self):
        return f'questionarios.view_{self.permission_base}'


class BaseResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView, BaseIndicadorMixin):
    """View base para resumos anuais de indicadores."""
    
    context_object_name = 'indicadores'
    
    def get_template_names(self):
        return [f'questionarios/{self.template_prefix}_resumo.html']
    
    def get_permission_required(self):
        return f'questionarios.view_{self.permission_base}'
    
    def get_queryset(self):
        ano = self.kwargs.get('ano')
        operadora = self.request.GET.get('operadora')
        queryset = self.model.objects.filter(ano=ano)
        if operadora:
            queryset = queryset.filter(operadora=operadora)
        return queryset.order_by('mes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.kwargs.get('ano')
        operadora = self.request.GET.get('operadora')
        indicadores = self.get_queryset()
        
        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['operadoras_choices'] = OPERADORAS_CHOICES
        
        # Calcular totais se o modelo tiver métodos de cálculo
        if hasattr(self.model, 'get_calculation_methods'):
            context.update(self._calculate_totals(indicadores))
        
        return context
    
    def _calculate_totals(self, indicadores):
        """Calcula totais trimestrais e anuais usando métodos do modelo."""
        calculation_methods = self.model.get_calculation_methods()
        
        # Totais trimestrais
        totais_trimestrais = []
        for trimestre in range(1, 5):
            meses = range((trimestre - 1) * 3 + 1, trimestre * 3 + 1)
            dados_trimestre = indicadores.filter(mes__in=meses)
            
            totals = {'trimestre': trimestre}
            for method_name, method_label in calculation_methods.items():
                total = sum(getattr(dado, method_name)() for dado in dados_trimestre if hasattr(dado, method_name))
                totals[f'total_{method_name}'] = total
            
            totais_trimestrais.append(totals)
        
        # Totais anuais
        totals_annual = {}
        for method_name, method_label in calculation_methods.items():
            total = sum(getattr(dado, method_name)() for dado in indicadores if hasattr(dado, method_name))
            totals_annual[f'total_{method_name}_anual'] = total
        
        return {
            'totais_trimestrais': totais_trimestrais,
            **totals_annual
        }


def create_indicator_views(model, form_class, template_prefix, url_namespace, permission_base):
    """
    Factory function para criar todas as views de um indicador.
    
    Args:
        model: Modelo do indicador
        form_class: Classe do formulário  
        template_prefix: Prefixo dos templates
        url_namespace: Namespace das URLs
        permission_base: Base das permissões
    
    Returns:
        dict: Dicionário com todas as views criadas
    """
    
    class IndicadorCreateView(BaseCreateView):
        model = model
        form_class = form_class
        template_prefix = template_prefix
        url_namespace = url_namespace
        permission_base = permission_base
    
    class IndicadorListView(FilteredListView):
        model = model
        form_class = form_class
        template_prefix = template_prefix
        url_namespace = url_namespace
        permission_base = permission_base
    
    class IndicadorUpdateView(BaseUpdateView):
        model = model
        form_class = form_class
        template_prefix = template_prefix
        url_namespace = url_namespace
        permission_base = permission_base
    
    class IndicadorDeleteView(BaseDeleteView):
        model = model
        form_class = form_class
        template_prefix = template_prefix
        url_namespace = url_namespace
        permission_base = permission_base
    
    class IndicadorDetailView(BaseDetailView):
        model = model
        form_class = form_class
        template_prefix = template_prefix
        url_namespace = url_namespace
        permission_base = permission_base
    
    class IndicadorResumoView(BaseResumoView):
        model = model
        form_class = form_class
        template_prefix = template_prefix
        url_namespace = url_namespace
        permission_base = permission_base
    
    return {
        'create': IndicadorCreateView,
        'list': IndicadorListView,
        'update': IndicadorUpdateView,
        'delete': IndicadorDeleteView,
        'detail': IndicadorDetailView,
        'resumo': IndicadorResumoView,
    } 