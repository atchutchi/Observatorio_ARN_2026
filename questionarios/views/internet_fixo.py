from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models import InternetFixoIndicador
from ..forms import InternetFixoForm
from .base_views import FilteredListView

class InternetFixoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = InternetFixoIndicador
    form_class = InternetFixoForm
    template_name = 'questionarios/internet_fixo_form.html'
    success_url = reverse_lazy('questionarios:internet_fixo_list')
    permission_required = 'questionarios.add_internetfixoindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class InternetFixoListView(FilteredListView):
    model = InternetFixoIndicador
    template_name = 'questionarios/internet_fixo_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_internetfixoindicador'

class InternetFixoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = InternetFixoIndicador
    form_class = InternetFixoForm
    template_name = 'questionarios/internet_fixo_form.html'
    success_url = reverse_lazy('questionarios:internet_fixo_list')
    permission_required = 'questionarios.change_internetfixoindicador'

class InternetFixoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = InternetFixoIndicador
    template_name = 'questionarios/internet_fixo_confirm_delete.html'
    success_url = reverse_lazy('questionarios:internet_fixo_list')
    permission_required = 'questionarios.delete_internetfixoindicador'

class InternetFixoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = InternetFixoIndicador
    template_name = 'questionarios/internet_fixo_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_internetfixoindicador'

class InternetFixoResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = InternetFixoIndicador
    template_name = 'questionarios/internet_fixo_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_internetfixoindicador'

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
            
            total_assinantes_radio = sum(dado.calcular_total_assinantes_radio() for dado in dados_trimestre)
            total_assinantes_ativos = sum(dado.calcular_total_assinantes_ativos() for dado in dados_trimestre)
            total_banda_larga = sum(dado.calcular_total_banda_larga() for dado in dados_trimestre)
            total_assinantes_categoria = sum(dado.calcular_total_assinantes_categoria() for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_assinantes_radio': total_assinantes_radio,
                'total_assinantes_ativos': total_assinantes_ativos,
                'total_banda_larga': total_banda_larga,
                'total_assinantes_categoria': total_assinantes_categoria
            })

        # Cálculos anuais
        total_assinantes_radio_anual = sum(dado.calcular_total_assinantes_radio() for dado in indicadores)
        total_assinantes_ativos_anual = sum(dado.calcular_total_assinantes_ativos() for dado in indicadores)
        total_banda_larga_anual = sum(dado.calcular_total_banda_larga() for dado in indicadores)
        total_assinantes_categoria_anual = sum(dado.calcular_total_assinantes_categoria() for dado in indicadores)

        context['operadora_selecionada'] = operadora
        context['ano'] = ano
        context['totais_trimestrais'] = totais_trimestrais
        context['total_assinantes_radio_anual'] = total_assinantes_radio_anual
        context['total_assinantes_ativos_anual'] = total_assinantes_ativos_anual
        context['total_banda_larga_anual'] = total_banda_larga_anual
        context['total_assinantes_categoria_anual'] = total_assinantes_categoria_anual

        return context