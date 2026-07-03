from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models.investimento import InvestimentoIndicador  # Importação específica do modelo
from ..forms.investimento import InvestimentoForm
from .base_views import FilteredListView


class InvestimentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = InvestimentoIndicador
    form_class = InvestimentoForm
    template_name = 'questionarios/investimento_form.html'
    success_url = reverse_lazy('questionarios:investimento_list')
    permission_required = 'questionarios.add_investimentoindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class InvestimentoListView(FilteredListView):
    model = InvestimentoIndicador
    template_name = 'questionarios/investimento_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_investimentoindicador'

class InvestimentoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = InvestimentoIndicador
    form_class = InvestimentoForm
    template_name = 'questionarios/investimento_form.html'
    success_url = reverse_lazy('questionarios:investimento_list')
    permission_required = 'questionarios.change_investimentoindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class InvestimentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = InvestimentoIndicador
    template_name = 'questionarios/investimento_confirm_delete.html'
    success_url = reverse_lazy('questionarios:investimento_list')
    permission_required = 'questionarios.delete_investimentoindicador'

class InvestimentoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = InvestimentoIndicador
    template_name = 'questionarios/investimento_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_investimentoindicador'

class InvestimentoResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = InvestimentoIndicador
    template_name = 'questionarios/investimento_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_investimentoindicador'

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

        # Cálculos trimestrais
        totais_trimestrais = []
        for trimestre in range(1, 5):
            meses = range((trimestre - 1) * 3 + 1, trimestre * 3 + 1)
            dados_trimestre = indicadores.filter(mes__in=meses)
            
            total_corporeo = sum(dado.calcular_total_corporeo() for dado in dados_trimestre)
            total_incorporeo = sum(dado.calcular_total_incorporeo() for dado in dados_trimestre)
            total_outros = sum(dado.calcular_total_outros() for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_corporeo': total_corporeo,
                'total_incorporeo': total_incorporeo,
                'total_outros': total_outros,
                'total_geral': total_corporeo + total_incorporeo + total_outros
            })

        # Cálculos anuais
        context['operadora_selecionada'] = operadora
        context['ano'] = ano
        context['totais_trimestrais'] = totais_trimestrais
        context['total_corporeo_anual'] = sum(dado.calcular_total_corporeo() for dado in indicadores)
        context['total_incorporeo_anual'] = sum(dado.calcular_total_incorporeo() for dado in indicadores)
        context['total_outros_anual'] = sum(dado.calcular_total_outros() for dado in indicadores)
        context['total_geral_anual'] = (
            context['total_corporeo_anual'] + 
            context['total_incorporeo_anual'] + 
            context['total_outros_anual']
        )

        return context