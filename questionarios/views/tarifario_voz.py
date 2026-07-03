from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models.tarifario_voz import TarifarioVozOrangeIndicador, TarifarioVozMTNIndicador
from ..forms.tarifario_voz import TarifarioVozOrangeForm, TarifarioVozMTNForm
from .base_views import FilteredListView

# Views para Orange
class TarifarioVozOrangeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TarifarioVozOrangeIndicador
    form_class = TarifarioVozOrangeForm
    template_name = 'questionarios/tarifario_orange_form.html'
    success_url = reverse_lazy('questionarios:tarifario_orange_list')
    permission_required = 'questionarios.add_tarifariovozorangeindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class TarifarioVozOrangeListView(FilteredListView):
    model = TarifarioVozOrangeIndicador
    template_name = 'questionarios/tarifario_orange_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_tarifariovozorangeindicador'

class TarifarioVozOrangeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TarifarioVozOrangeIndicador
    form_class = TarifarioVozOrangeForm
    template_name = 'questionarios/tarifario_orange_form.html'
    success_url = reverse_lazy('questionarios:tarifario_orange_list')
    permission_required = 'questionarios.change_tarifariovozorangeindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class TarifarioVozOrangeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TarifarioVozOrangeIndicador
    template_name = 'questionarios/tarifario_orange_confirm_delete.html'
    success_url = reverse_lazy('questionarios:tarifario_orange_list')
    permission_required = 'questionarios.delete_tarifariovozorangeindicador'

class TarifarioVozOrangeDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TarifarioVozOrangeIndicador
    template_name = 'questionarios/tarifario_orange_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_tarifariovozorangeindicador'

class TarifarioVozOrangeResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TarifarioVozOrangeIndicador
    template_name = 'questionarios/tarifario_orange_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_tarifariovozorangeindicador'

    def get_queryset(self):
        ano = self.kwargs.get('ano')
        return TarifarioVozOrangeIndicador.objects.filter(ano=ano).order_by('mes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.kwargs.get('ano')
        indicadores = self.get_queryset()

        # Cálculos trimestrais
        totais_trimestrais = []
        for trimestre in range(1, 5):
            meses = range((trimestre - 1) * 3 + 1, trimestre * 3 + 1)
            dados_trimestre = indicadores.filter(mes__in=meses)
            
            # Cálculos específicos Orange
            total_internet_prepago = sum(dado.dongle_3g + dado.dongle_4g + dado.airbox_4g + dado.flybox_4g + dado.flybox_4g_plus for dado in dados_trimestre)
            total_internet_residencial = sum(dado.casa_zen_2mbits_adesao + dado.casa_conforto_4mbits_adesao + dado.casabox_2mbits_adesao + dado.casabox_5mbits_adesao for dado in dados_trimestre)
            total_passes = sum(
                dado.pass_ilimite_1h + dado.pass_ilimite_3h + dado.pass_ilimite_8h + 
                dado.pass_ilimite_dimanche + dado.pass_ilimite_nuit + dado.pass_jours_ferie +
                dado.pass_30_mo + dado.pass_75_mo + dado.pass_150_mo + dado.pass_250_mo +
                dado.pass_500_mo + dado.pass_600_mo + dado.pass_1_5_go + dado.pass_3_go +
                dado.pass_10_go + dado.pass_18_go + dado.pass_35_go + dado.pass_100_go +
                dado.pass_400_mo + dado.pass_1_go
                for dado in dados_trimestre
            )
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_internet_prepago': total_internet_prepago,
                'total_internet_residencial': total_internet_residencial,
                'total_passes': total_passes,
                'media_tarifa_onnet': sum(dado.tarifa_orange_livre_6h_22h for dado in dados_trimestre) / len(dados_trimestre) if dados_trimestre else 0,
                'media_tarifa_offnet_local': sum(dado.tarifa_offnet_orange_livre for dado in dados_trimestre) / len(dados_trimestre) if dados_trimestre else 0,
            })

        # Cálculos anuais
        total_internet_prepago_anual = sum(dado.dongle_3g + dado.dongle_4g + dado.airbox_4g + dado.flybox_4g + dado.flybox_4g_plus for dado in indicadores)
        total_internet_residencial_anual = sum(dado.casa_zen_2mbits_adesao + dado.casa_conforto_4mbits_adesao + dado.casabox_2mbits_adesao + dado.casabox_5mbits_adesao for dado in indicadores)
        total_passes_anual = sum(
            dado.pass_ilimite_1h + dado.pass_ilimite_3h + dado.pass_ilimite_8h + 
            dado.pass_ilimite_dimanche + dado.pass_ilimite_nuit + dado.pass_jours_ferie +
            dado.pass_30_mo + dado.pass_75_mo + dado.pass_150_mo + dado.pass_250_mo +
            dado.pass_500_mo + dado.pass_600_mo + dado.pass_1_5_go + dado.pass_3_go +
            dado.pass_10_go + dado.pass_18_go + dado.pass_35_go + dado.pass_100_go +
            dado.pass_400_mo + dado.pass_1_go
            for dado in indicadores
        )

        context['ano'] = ano
        context['totais_trimestrais'] = totais_trimestrais
        context['total_internet_prepago_anual'] = total_internet_prepago_anual
        context['total_internet_residencial_anual'] = total_internet_residencial_anual
        context['total_passes_anual'] = total_passes_anual
        return context

# Views para TELECEL
class TarifarioVozMTNCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TarifarioVozMTNIndicador
    form_class = TarifarioVozMTNForm
    template_name = 'questionarios/tarifario_telecel_form.html'
    success_url = reverse_lazy('questionarios:tarifario_telecel_list')
    permission_required = 'questionarios.add_tarifariovoztelecelindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class TarifarioVozMTNListView(FilteredListView):
    model = TarifarioVozMTNIndicador
    template_name = 'questionarios/tarifario_telecel_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_tarifariovoztelecelindicador'

class TarifarioVozMTNUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TarifarioVozMTNIndicador
    form_class = TarifarioVozMTNForm
    template_name = 'questionarios/tarifario_telecel_form.html'
    success_url = reverse_lazy('questionarios:tarifario_telecel_list')
    permission_required = 'questionarios.change_tarifariovoztelecelindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class TarifarioVozMTNDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TarifarioVozMTNIndicador
    template_name = 'questionarios/tarifario_telecel_confirm_delete.html'
    success_url = reverse_lazy('questionarios:tarifario_telecel_list')
    permission_required = 'questionarios.delete_tarifariovoztelecelindicador'

class TarifarioVozMTNDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TarifarioVozMTNIndicador
    template_name = 'questionarios/tarifario_telecel_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_tarifariovoztelecelindicador'

class TarifarioVozMTNResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TarifarioVozMTNIndicador
    template_name = 'questionarios/tarifario_telecel_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_tarifariovoztelecelindicador'

    def get_queryset(self):
        ano = self.kwargs.get('ano')
        return TarifarioVozMTNIndicador.objects.filter(ano=ano).order_by('mes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.kwargs.get('ano')
        indicadores = self.get_queryset()

        # Cálculos trimestrais
        totais_trimestrais = []
        for trimestre in range(1, 5):
            meses = range((trimestre - 1) * 3 + 1, trimestre * 3 + 1)
            dados_trimestre = indicadores.filter(mes__in=meses)
            
            # Cálculos específicos MTN
            total_equipamentos = sum(dado.huawei_4g_lte + dado.huawei_mobile_wifi_4g for dado in dados_trimestre)
            
            total_pacotes_diarios = sum(
                dado.pacote_30mb + dado.pacote_100mb + dado.pacote_300mb + 
                dado.pacote_1gb for dado in dados_trimestre
            )
            
            total_pacotes_semanais = sum(
                dado.pacote_650mb + dado.pacote_1000mb for dado in dados_trimestre
            )
            
            total_pacotes_mensais = sum(
                dado.pacote_1_5gb + dado.pacote_10gb + dado.pacote_18gb + 
                dado.pacote_30gb + dado.pacote_50gb + dado.pacote_60gb + 
                dado.pacote_120gb for dado in dados_trimestre
            )
            
            total_pacotes_yello = sum(
                dado.pacote_yello_350mb + dado.pacote_yello_1_5gb + 
                dado.pacote_yello_1_5gb_7dias for dado in dados_trimestre
            )
            
            total_pacotes_ilimitados = sum(
                dado.pacote_1hora + dado.pacote_3horas + dado.pacote_9horas 
                for dado in dados_trimestre
            )
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_equipamentos': total_equipamentos,
                'total_pacotes_diarios': total_pacotes_diarios,
                'total_pacotes_semanais': total_pacotes_semanais,
                'total_pacotes_mensais': total_pacotes_mensais,
                'total_pacotes_yello': total_pacotes_yello,
                'total_pacotes_ilimitados': total_pacotes_ilimitados
            })

        # Cálculos anuais
        context['ano'] = ano
        context['totais_trimestrais'] = totais_trimestrais
        context['total_equipamentos_anual'] = sum(dado.huawei_4g_lte + dado.huawei_mobile_wifi_4g for dado in indicadores)
        context['total_pacotes_diarios_anual'] = sum(dado.pacote_30mb + dado.pacote_100mb + dado.pacote_300mb + dado.pacote_1gb for dado in indicadores)
        context['total_pacotes_semanais_anual'] = sum(dado.pacote_650mb + dado.pacote_1000mb for dado in indicadores)
        context['total_pacotes_mensais_anual'] = sum(dado.pacote_1_5gb + dado.pacote_10gb + dado.pacote_18gb + dado.pacote_30gb + dado.pacote_50gb + dado.pacote_60gb + dado.pacote_120gb for dado in indicadores)
        context['total_pacotes_yello_anual'] = sum(dado.pacote_yello_350mb + dado.pacote_yello_1_5gb + dado.pacote_yello_1_5gb_7dias for dado in indicadores)
        context['total_pacotes_ilimitados_anual'] = sum(dado.pacote_1hora + dado.pacote_3horas + dado.pacote_9horas for dado in indicadores)
        return context