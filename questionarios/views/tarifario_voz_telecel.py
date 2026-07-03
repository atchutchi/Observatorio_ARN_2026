from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models import TarifarioVozTelecelIndicador
from ..forms import TarifarioVozTelecelForm
from .base_views import FilteredListView

# Views para TELECEL (mirrored from TELECEL)
class TarifarioVozTelecelCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TarifarioVozTelecelIndicador
    form_class = TarifarioVozTelecelForm
    template_name = 'questionarios/tarifario_telecel_form.html' # Use specific template
    success_url = reverse_lazy('questionarios:tarifario_telecel_list')
    permission_required = 'questionarios.add_tarifariovoztelecelindicador' # Needs new permission

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class TarifarioVozTelecelListView(FilteredListView):
    model = TarifarioVozTelecelIndicador
    template_name = 'questionarios/tarifario_telecel_list.html' # Use specific template
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_tarifariovoztelecelindicador' # Needs new permission

class TarifarioVozTelecelUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TarifarioVozTelecelIndicador
    form_class = TarifarioVozTelecelForm
    template_name = 'questionarios/tarifario_telecel_form.html' # Use specific template
    success_url = reverse_lazy('questionarios:tarifario_telecel_list')
    permission_required = 'questionarios.change_tarifariovoztelecelindicador' # Needs new permission

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class TarifarioVozTelecelDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TarifarioVozTelecelIndicador
    template_name = 'questionarios/tarifario_telecel_confirm_delete.html' # Use specific template
    success_url = reverse_lazy('questionarios:tarifario_telecel_list')
    permission_required = 'questionarios.delete_tarifariovoztelecelindicador' # Needs new permission

class TarifarioVozTelecelDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TarifarioVozTelecelIndicador
    template_name = 'questionarios/tarifario_telecel_detail.html' # Use specific template
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_tarifariovoztelecelindicador' # Needs new permission

# Resumo view might need adjustments based on Telecel-specific calculations if any
# For now, mirror TELECEL structure for calculations
class TarifarioVozTelecelResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TarifarioVozTelecelIndicador
    template_name = 'questionarios/tarifario_telecel_resumo.html' # Use specific template
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_tarifariovoztelecelindicador'

    def get_queryset(self):
        ano = self.kwargs.get('ano')
        return TarifarioVozTelecelIndicador.objects.filter(ano=ano).order_by('mes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.kwargs.get('ano')
        indicadores = self.get_queryset()

        # Cálculos trimestrais (mirroring TELECEL)
        totais_trimestrais = []
        for trimestre in range(1, 5):
            meses = range((trimestre - 1) * 3 + 1, trimestre * 3 + 1)
            dados_trimestre = indicadores.filter(mes__in=meses)
            
            total_equipamentos = sum(dado.huawei_4g_lte + dado.huawei_mobile_wifi_4g for dado in dados_trimestre)
            total_pacotes_diarios = sum(dado.pacote_30mb + dado.pacote_100mb + dado.pacote_300mb + dado.pacote_1gb for dado in dados_trimestre)
            total_pacotes_semanais = sum(dado.pacote_650mb + dado.pacote_1000mb for dado in dados_trimestre)
            total_pacotes_mensais = sum(dado.pacote_1_5gb + dado.pacote_10gb + dado.pacote_18gb + dado.pacote_30gb + dado.pacote_50gb + dado.pacote_60gb + dado.pacote_120gb for dado in dados_trimestre)
            total_pacotes_yello = sum(dado.pacote_yello_350mb + dado.pacote_yello_1_5gb + dado.pacote_yello_1_5gb_7dias for dado in dados_trimestre)
            total_pacotes_ilimitados = sum(dado.pacote_1hora + dado.pacote_3horas + dado.pacote_9horas for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_equipamentos': total_equipamentos,
                'total_pacotes_diarios': total_pacotes_diarios,
                'total_pacotes_semanais': total_pacotes_semanais,
                'total_pacotes_mensais': total_pacotes_mensais,
                'total_pacotes_yello': total_pacotes_yello,
                'total_pacotes_ilimitados': total_pacotes_ilimitados
            })

        # Cálculos anuais (mirroring TELECEL)
        context['ano'] = ano
        context['totais_trimestrais'] = totais_trimestrais
        context['total_equipamentos_anual'] = sum(dado.huawei_4g_lte + dado.huawei_mobile_wifi_4g for dado in indicadores)
        context['total_pacotes_diarios_anual'] = sum(dado.pacote_30mb + dado.pacote_100mb + dado.pacote_300mb + dado.pacote_1gb for dado in indicadores)
        context['total_pacotes_semanais_anual'] = sum(dado.pacote_650mb + dado.pacote_1000mb for dado in indicadores)
        context['total_pacotes_mensais_anual'] = sum(dado.pacote_1_5gb + dado.pacote_10gb + dado.pacote_18gb + dado.pacote_30gb + dado.pacote_50gb + dado.pacote_60gb + dado.pacote_120gb for dado in indicadores)
        context['total_pacotes_yello_anual'] = sum(dado.pacote_yello_350mb + dado.pacote_yello_1_5gb + dado.pacote_yello_1_5gb_7dias for dado in indicadores)
        context['total_pacotes_ilimitados_anual'] = sum(dado.pacote_1hora + dado.pacote_3horas + dado.pacote_9horas for dado in indicadores)
        return context 