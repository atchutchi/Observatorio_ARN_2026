from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models.trafego_roaming_internacional import TrafegoRoamingInternacionalIndicador
from ..forms.trafego_roaming_internacional import TrafegoRoamingInternacionalForm
from .base_views import FilteredListView

class TrafegoRoamingInternacionalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrafegoRoamingInternacionalIndicador
    form_class = TrafegoRoamingInternacionalForm
    template_name = 'questionarios/trafego_roaming_internacional_form.html'
    success_url = reverse_lazy('questionarios:trafego_roaming_internacional_list')
    permission_required = 'questionarios.add_trafegoroaminginternacionalindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class TrafegoRoamingInternacionalListView(FilteredListView):
    model = TrafegoRoamingInternacionalIndicador
    template_name = 'questionarios/trafego_roaming_internacional_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_trafegoroaminginternacionalindicador'

class TrafegoRoamingInternacionalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrafegoRoamingInternacionalIndicador
    form_class = TrafegoRoamingInternacionalForm
    template_name = 'questionarios/trafego_roaming_internacional_form.html'
    success_url = reverse_lazy('questionarios:trafego_roaming_internacional_list')
    permission_required = 'questionarios.change_trafegoroaminginternacionalindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class TrafegoRoamingInternacionalDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TrafegoRoamingInternacionalIndicador
    template_name = 'questionarios/trafego_roaming_internacional_confirm_delete.html'
    success_url = reverse_lazy('questionarios:trafego_roaming_internacional_list')
    permission_required = 'questionarios.delete_trafegoroaminginternacionalindicador'

class TrafegoRoamingInternacionalDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TrafegoRoamingInternacionalIndicador
    template_name = 'questionarios/trafego_roaming_internacional_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_trafegoroaminginternacionalindicador'

class TrafegoRoamingInternacionalResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TrafegoRoamingInternacionalIndicador
    template_name = 'questionarios/trafego_roaming_internacional_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_trafegoroaminginternacionalindicador'

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
            
            total_chamadas_in = sum(dado.chamadas_originadas_rede + dado.chamadas_terminadas_rede for dado in dados_trimestre)
            total_minutos_in = sum(dado.minutos_originados_rede + dado.minutos_terminados_rede for dado in dados_trimestre)
            total_mensagens_in = sum(dado.mensagens_escritas_enviadas + dado.mensagens_escritas_recebidas for dado in dados_trimestre)
            total_sessoes_in = sum(dado.sessoes_acesso_internet for dado in dados_trimestre)
            total_volume_in = sum(dado.volume_acesso_internet for dado in dados_trimestre)

            total_chamadas_out = sum(dado.chamadas_originadas_operador_roaming + dado.chamadas_terminadas_operador_roaming for dado in dados_trimestre)
            total_minutos_out = sum(dado.minutos_originados_operador_roaming + dado.minutos_terminados_operador_roaming for dado in dados_trimestre)
            total_mensagens_out = sum(dado.mensagens_escritas_enviadas_out for dado in dados_trimestre)
            total_sessoes_out = sum(dado.sessoes_acesso_internet_out for dado in dados_trimestre)
            total_volume_out = sum(dado.volume_acesso_internet_out for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_chamadas_in': total_chamadas_in,
                'total_minutos_in': total_minutos_in,
                'total_mensagens_in': total_mensagens_in,
                'total_sessoes_in': total_sessoes_in,
                'total_volume_in': total_volume_in,
                'total_chamadas_out': total_chamadas_out,
                'total_minutos_out': total_minutos_out,
                'total_mensagens_out': total_mensagens_out,
                'total_sessoes_out': total_sessoes_out,
                'total_volume_out': total_volume_out
            })

        # Cálculos anuais
        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['totais_trimestrais'] = totais_trimestrais
        
        # IN
        context['total_chamadas_in_anual'] = sum(dado.chamadas_originadas_rede + dado.chamadas_terminadas_rede for dado in indicadores)
        context['total_minutos_in_anual'] = sum(dado.minutos_originados_rede + dado.minutos_terminados_rede for dado in indicadores)
        context['total_mensagens_in_anual'] = sum(dado.mensagens_escritas_enviadas + dado.mensagens_escritas_recebidas for dado in indicadores)
        context['total_sessoes_in_anual'] = sum(dado.sessoes_acesso_internet for dado in indicadores)
        context['total_volume_in_anual'] = sum(dado.volume_acesso_internet for dado in indicadores)
        
        # OUT
        context['total_chamadas_out_anual'] = sum(dado.chamadas_originadas_operador_roaming + dado.chamadas_terminadas_operador_roaming for dado in indicadores)
        context['total_minutos_out_anual'] = sum(dado.minutos_originados_operador_roaming + dado.minutos_terminados_operador_roaming for dado in indicadores)
        context['total_mensagens_out_anual'] = sum(dado.mensagens_escritas_enviadas_out for dado in indicadores)
        context['total_sessoes_out_anual'] = sum(dado.sessoes_acesso_internet_out for dado in indicadores)
        context['total_volume_out_anual'] = sum(dado.volume_acesso_internet_out for dado in indicadores)

        return context