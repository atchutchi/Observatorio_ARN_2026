from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from ..models.trafego_terminado import TrafegoTerminadoIndicador
from ..forms.trafego_terminado import TrafegoTerminadoForm
from .base_views import FilteredListView

class TrafegoTerminadoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrafegoTerminadoIndicador
    form_class = TrafegoTerminadoForm
    template_name = 'questionarios/trafego_terminado_form.html'
    success_url = reverse_lazy('questionarios:trafego_terminado_list')
    permission_required = 'questionarios.add_trafegoterminadoindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class TrafegoTerminadoListView(FilteredListView):
    model = TrafegoTerminadoIndicador
    template_name = 'questionarios/trafego_terminado_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_trafegoterminadoindicador'

class TrafegoTerminadoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrafegoTerminadoIndicador
    form_class = TrafegoTerminadoForm
    template_name = 'questionarios/trafego_terminado_form.html'
    success_url = reverse_lazy('questionarios:trafego_terminado_list')
    permission_required = 'questionarios.change_trafegoterminadoindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class TrafegoTerminadoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TrafegoTerminadoIndicador
    template_name = 'questionarios/trafego_terminado_confirm_delete.html'
    success_url = reverse_lazy('questionarios:trafego_terminado_list')
    permission_required = 'questionarios.delete_trafegoterminadoindicador'

class TrafegoTerminadoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TrafegoTerminadoIndicador
    template_name = 'questionarios/trafego_terminado_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_trafegoterminadoindicador'

class TrafegoTerminadoResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TrafegoTerminadoIndicador
    template_name = 'questionarios/trafego_terminado_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_trafegoterminadoindicador'

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
            
            total_chamadas = sum(dado.calcular_total_chamadas() for dado in dados_trimestre)
            total_minutos = sum(dado.calcular_total_minutos() for dado in dados_trimestre)
            total_sms = sum(dado.calcular_total_sms() for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_chamadas': total_chamadas,
                'total_minutos': total_minutos,
                'total_sms': total_sms
            })

        # Cálculos anuais
        total_chamadas_anual = sum(dado.calcular_total_chamadas() for dado in indicadores)
        total_minutos_anual = sum(dado.calcular_total_minutos() for dado in indicadores)
        total_sms_anual = sum(dado.calcular_total_sms() for dado in indicadores)

        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['totais_trimestrais'] = totais_trimestrais
        context['total_chamadas_anual'] = total_chamadas_anual
        context['total_minutos_anual'] = total_minutos_anual
        context['total_sms_anual'] = total_sms_anual

        return context