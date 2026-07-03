from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from ..models.emprego import EmpregoIndicador
from ..forms.emprego import EmpregoForm
from .base_views import FilteredListView

class EmpregoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = EmpregoIndicador
    form_class = EmpregoForm
    template_name = 'questionarios/emprego_form.html'
    success_url = reverse_lazy('questionarios:emprego_list')
    permission_required = 'questionarios.add_empregoindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class EmpregoListView(FilteredListView):
    model = EmpregoIndicador
    template_name = 'questionarios/emprego_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_empregoindicador'

class EmpregoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = EmpregoIndicador
    form_class = EmpregoForm
    template_name = 'questionarios/emprego_form.html'
    success_url = reverse_lazy('questionarios:emprego_list')
    permission_required = 'questionarios.change_empregoindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        return super().form_valid(form)

class EmpregoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = EmpregoIndicador
    template_name = 'questionarios/emprego_confirm_delete.html'
    success_url = reverse_lazy('questionarios:emprego_list')
    permission_required = 'questionarios.delete_empregoindicador'

class EmpregoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = EmpregoIndicador
    template_name = 'questionarios/emprego_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_empregoindicador'

class EmpregoResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = EmpregoIndicador
    template_name = 'questionarios/emprego_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_empregoindicador'

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
            
            total_emprego_direto = sum(dado.calcular_total_emprego_direto() for dado in dados_trimestre)
            total_nacionais = sum(dado.calcular_total_nacionais() for dado in dados_trimestre)
            total_homens = sum(dado.nacionais_homem for dado in dados_trimestre)
            total_mulheres = sum(dado.nacionais_mulher for dado in dados_trimestre)
            total_emprego_indireto = sum(dado.calcular_total_emprego_indireto() for dado in dados_trimestre)
            
            totais_trimestrais.append({
                'trimestre': trimestre,
                'total_emprego_direto': total_emprego_direto / len(dados_trimestre) if dados_trimestre else 0,
                'total_nacionais': total_nacionais / len(dados_trimestre) if dados_trimestre else 0,
                'total_homens': total_homens / len(dados_trimestre) if dados_trimestre else 0,
                'total_mulheres': total_mulheres / len(dados_trimestre) if dados_trimestre else 0,
                'total_emprego_indireto': total_emprego_indireto / len(dados_trimestre) if dados_trimestre else 0,
                'percentual_homens': (total_homens / total_nacionais * 100) if total_nacionais else 0,
                'percentual_mulheres': (total_mulheres / total_nacionais * 100) if total_nacionais else 0
            })

        # Cálculos anuais
        dados_anuais = len(indicadores)
        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['totais_trimestrais'] = totais_trimestrais
        context['total_emprego_direto_anual'] = sum(dado.calcular_total_emprego_direto() for dado in indicadores) / dados_anuais if dados_anuais else 0
        context['total_nacionais_anual'] = sum(dado.calcular_total_nacionais() for dado in indicadores) / dados_anuais if dados_anuais else 0
        context['total_homens_anual'] = sum(dado.nacionais_homem for dado in indicadores) / dados_anuais if dados_anuais else 0
        context['total_mulheres_anual'] = sum(dado.nacionais_mulher for dado in indicadores) / dados_anuais if dados_anuais else 0
        context['total_emprego_indireto_anual'] = sum(dado.calcular_total_emprego_indireto() for dado in indicadores) / dados_anuais if dados_anuais else 0
        
        total_nacionais = context['total_nacionais_anual']
        context['percentual_homens_anual'] = (context['total_homens_anual'] / total_nacionais * 100) if total_nacionais else 0
        context['percentual_mulheres_anual'] = (context['total_mulheres_anual'] / total_nacionais * 100) if total_nacionais else 0

        return context