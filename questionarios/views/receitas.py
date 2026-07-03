# views/receitas.py
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from ..models.receitas import ReceitasIndicador
from ..forms.receitas import ReceitasForm
from .base_views import FilteredListView

class ReceitasCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ReceitasIndicador
    form_class = ReceitasForm
    template_name = 'questionarios/receitas_form.html'
    success_url = reverse_lazy('questionarios:receitas_list')
    permission_required = 'questionarios.add_receitasindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class ReceitasListView(FilteredListView):
    model = ReceitasIndicador
    template_name = 'questionarios/receitas_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_receitasindicador'

class ReceitasUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ReceitasIndicador
    form_class = ReceitasForm
    template_name = 'questionarios/receitas_form.html'
    success_url = reverse_lazy('questionarios:receitas_list')
    permission_required = 'questionarios.change_receitasindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class ReceitasDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ReceitasIndicador
    template_name = 'questionarios/receitas_confirm_delete.html'
    success_url = reverse_lazy('questionarios:receitas_list')
    permission_required = 'questionarios.delete_receitasindicador'

class ReceitasDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ReceitasIndicador
    template_name = 'questionarios/receitas_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_receitasindicador'

class ReceitasResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ReceitasIndicador
    template_name = 'questionarios/receitas_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_receitasindicador'

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
            
            total_receitas_retalhistas = sum(dado.calcular_total_receitas_retalhistas() for dado in dados_trimestre)
            total_receitas_voz = sum(dado.calcular_total_receitas_voz() for dado in dados_trimestre)
            total_receitas_dados = sum(dado.calcular_total_receitas_dados() for dado in dados_trimestre)
            total_receitas_grossistas = sum(dado.calcular_total_receitas_grossistas() for dado in dados_trimestre)
            total_receitas_internacional = sum(dado.calcular_total_receitas_internacional() for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_receitas_retalhistas': total_receitas_retalhistas,
                'total_receitas_voz': total_receitas_voz,
                'total_receitas_dados': total_receitas_dados,
                'total_receitas_grossistas': total_receitas_grossistas,
                'total_receitas_internacional': total_receitas_internacional,
                'total_receitas': total_receitas_retalhistas + total_receitas_grossistas
            })

        # Cálculos anuais
        total_receitas_retalhistas_anual = sum(dado.calcular_total_receitas_retalhistas() for dado in indicadores)
        total_receitas_voz_anual = sum(dado.calcular_total_receitas_voz() for dado in indicadores)
        total_receitas_dados_anual = sum(dado.calcular_total_receitas_dados() for dado in indicadores)
        total_receitas_grossistas_anual = sum(dado.calcular_total_receitas_grossistas() for dado in indicadores)
        total_receitas_internacional_anual = sum(dado.calcular_total_receitas_internacional() for dado in indicadores)
        total_receitas_anual = total_receitas_retalhistas_anual + total_receitas_grossistas_anual

        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['totais_trimestrais'] = totais_trimestrais
        context['total_receitas_retalhistas_anual'] = total_receitas_retalhistas_anual
        context['total_receitas_voz_anual'] = total_receitas_voz_anual
        context['total_receitas_dados_anual'] = total_receitas_dados_anual
        context['total_receitas_grossistas_anual'] = total_receitas_grossistas_anual
        context['total_receitas_internacional_anual'] = total_receitas_internacional_anual
        context['total_receitas_anual'] = total_receitas_anual

        return context