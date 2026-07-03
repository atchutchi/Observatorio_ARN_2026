from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from ..models import AssinantesIndicador
from ..forms import AssinantesIndicadorForm
from .base_views import FilteredListView

class AssinantesCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AssinantesIndicador
    form_class = AssinantesIndicadorForm
    template_name = 'questionarios/assinantes_form.html'
    success_url = reverse_lazy('questionarios:assinantes_list')
    permission_required = 'questionarios.add_assinantesindicador'

    # Assinantes model doesn't have criado_por/atualizado_por
    # def form_valid(self, form):
    #     form.instance.criado_por = self.request.user
    #     return super().form_valid(form)

class AssinantesListView(FilteredListView):
    model = AssinantesIndicador
    template_name = 'questionarios/assinantes_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_assinantesindicador'

class AssinantesUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = AssinantesIndicador
    form_class = AssinantesIndicadorForm
    template_name = 'questionarios/assinantes_form.html'
    success_url = reverse_lazy('questionarios:assinantes_list')
    permission_required = 'questionarios.change_assinantesindicador'

    # def form_valid(self, form):
    #     form.instance.atualizado_por = self.request.user
    #     return super().form_valid(form)

class AssinantesDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AssinantesIndicador
    template_name = 'questionarios/assinantes_confirm_delete.html'
    success_url = reverse_lazy('questionarios:assinantes_list')
    permission_required = 'questionarios.delete_assinantesindicador'

class AssinantesDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = AssinantesIndicador
    template_name = 'questionarios/assinantes_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_assinantesindicador'

class AssinantesResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = AssinantesIndicador
    template_name = 'questionarios/assinantes_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_assinantesindicador'

    def get_queryset(self):
        ano = self.kwargs.get('ano')
        operadora = self.request.GET.get('operadora')
        queryset = AssinantesIndicador.objects.filter(ano=ano)
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
            
            total_pre_pago = sum(dado.assinantes_pre_pago or 0 for dado in dados_trimestre)
            total_pos_pago = sum(dado.assinantes_pos_pago or 0 for dado in dados_trimestre)
            total_fixo = sum(dado.assinantes_fixo or 0 for dado in dados_trimestre)
            total_internet_movel = sum(dado.assinantes_internet_movel or 0 for dado in dados_trimestre)
            total_internet_fixa = sum(dado.assinantes_internet_fixa or 0 for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_pre_pago': total_pre_pago,
                'total_pos_pago': total_pos_pago,
                'total_fixo': total_fixo,
                'total_internet_movel': total_internet_movel,
                'total_internet_fixa': total_internet_fixa,
                'total_geral': total_pre_pago + total_pos_pago + total_fixo + total_internet_movel + total_internet_fixa
            })

        # Cálculos anuais
        total_pre_pago_anual = sum(dado.assinantes_pre_pago or 0 for dado in indicadores)
        total_pos_pago_anual = sum(dado.assinantes_pos_pago or 0 for dado in indicadores)
        total_fixo_anual = sum(dado.assinantes_fixo or 0 for dado in indicadores)
        total_internet_movel_anual = sum(dado.assinantes_internet_movel or 0 for dado in indicadores)
        total_internet_fixa_anual = sum(dado.assinantes_internet_fixa or 0 for dado in indicadores)

        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['totais_trimestrais'] = totais_trimestrais
        context['total_pre_pago_anual'] = total_pre_pago_anual
        context['total_pos_pago_anual'] = total_pos_pago_anual
        context['total_fixo_anual'] = total_fixo_anual
        context['total_internet_movel_anual'] = total_internet_movel_anual
        context['total_internet_fixa_anual'] = total_internet_fixa_anual
        context['total_geral_anual'] = total_pre_pago_anual + total_pos_pago_anual + total_fixo_anual + total_internet_movel_anual + total_internet_fixa_anual

        return context 