from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models.lbi import LBIIndicador
from ..forms.lbi import LBIForm
from .base_views import FilteredListView

class LBICreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = LBIIndicador
    form_class = LBIForm
    template_name = 'questionarios/lbi_form.html'
    success_url = reverse_lazy('questionarios:lbi_list')
    permission_required = 'questionarios.add_lbiindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class LBIListView(FilteredListView):
    model = LBIIndicador
    template_name = 'questionarios/lbi_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_lbiindicador'

class LBIUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = LBIIndicador
    form_class = LBIForm
    template_name = 'questionarios/lbi_form.html'
    success_url = reverse_lazy('questionarios:lbi_list')
    permission_required = 'questionarios.change_lbiindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class LBIDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = LBIIndicador
    template_name = 'questionarios/lbi_confirm_delete.html'
    success_url = reverse_lazy('questionarios:lbi_list')
    permission_required = 'questionarios.delete_lbiindicador'

class LBIDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = LBIIndicador
    template_name = 'questionarios/lbi_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_lbiindicador'

class LBIResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = LBIIndicador
    template_name = 'questionarios/lbi_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_lbiindicador'

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
            
            total_tecnologia = sum(dado.calcular_total_tecnologia() for dado in dados_trimestre)
            total_down = sum(dado.calcular_total_down() for dado in dados_trimestre)
            total_up = sum(dado.calcular_total_up() for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_tecnologia': total_tecnologia,
                'total_down': total_down,
                'total_up': total_up,
            })

        # Cálculos anuais
        total_tecnologia_anual = sum(dado.calcular_total_tecnologia() for dado in indicadores)
        total_down_anual = sum(dado.calcular_total_down() for dado in indicadores)
        total_up_anual = sum(dado.calcular_total_up() for dado in indicadores)

        context['operadora_selecionada'] = operadora
        context['ano'] = ano
        context['totais_trimestrais'] = totais_trimestrais
        context['total_tecnologia_anual'] = total_tecnologia_anual
        context['total_down_anual'] = total_down_anual
        context['total_up_anual'] = total_up_anual

        return context