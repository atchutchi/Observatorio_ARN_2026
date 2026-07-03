"""
Views para Tráfego Originado com cálculos otimizados para KPI ARN.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.db.models import Sum, Q, F, DecimalField, BigIntegerField, Case, When, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from decimal import Decimal

from ..models.trafego_originado import TrafegoOriginadoIndicador
from ..forms.trafego_originado import TrafegoOriginadoForm
from .base_views import FilteredListView

class TrafegoOriginadoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrafegoOriginadoIndicador
    form_class = TrafegoOriginadoForm
    template_name = 'questionarios/trafego_originado_form.html'
    success_url = reverse_lazy('questionarios:trafego_originado_list')
    permission_required = 'questionarios.add_trafegooriginadoindicador'

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, 'Indicador de Tráfego Originado criado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar indicador. Verifique os dados.')
        return super().form_invalid(form)

class TrafegoOriginadoListView(FilteredListView):
    model = TrafegoOriginadoIndicador
    template_name = 'questionarios/trafego_originado_list.html'
    context_object_name = 'object_list'
    permission_required = 'questionarios.view_trafegooriginadoindicador'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas resumidas usando agregação
        queryset = self.get_queryset()
        
        if queryset.exists():
            # Totais de dados
            totals_data = queryset.aggregate(
                # Total de dados em MB
                total_dados_mb=Coalesce(
                    Sum(F('trafego_dados_2g_mbytes') + 
                        F('trafego_dados_3g_upgrade_mbytes') + 
                        F('internet_3g_mbytes') +
                        F('trafego_dados_4g_mbytes') + 
                        F('internet_4g_mbytes')),
                    0,
                    output_field=BigIntegerField()
                ),
                # Total de sessões
                total_sessoes=Coalesce(
                    Sum(F('trafego_dados_2g_sessoes') +
                        F('trafego_dados_3g_upgrade_sessoes') +
                        F('trafego_dados_4g_sessoes')),
                    0,
                    output_field=BigIntegerField()
                ),
                # Total SMS
                total_sms=Coalesce(
                    Sum('sms_total'),
                    0,
                    output_field=BigIntegerField()
                ),
                # Total minutos voz
                total_voz_minutos=Coalesce(
                    Sum('voz_total_minutos'),
                    0,
                    output_field=BigIntegerField()
                ),
                # Total chamadas
                total_chamadas=Coalesce(
                    Sum('chamadas_total'),
                    0,
                    output_field=BigIntegerField()
                )
            )
            
            # Converter MB para GB para exibição
            totals_data['total_dados_gb'] = totals_data['total_dados_mb'] / 1024 if totals_data['total_dados_mb'] else 0
            
            # Calcular médias
            count = queryset.count()
            totals_data['media_sms_mes'] = totals_data['total_sms'] / count if count > 0 else 0
            totals_data['media_minutos_mes'] = totals_data['total_voz_minutos'] / count if count > 0 else 0
            
            context['estatisticas'] = totals_data
        
        return context

class TrafegoOriginadoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrafegoOriginadoIndicador
    form_class = TrafegoOriginadoForm
    template_name = 'questionarios/trafego_originado_form.html'
    success_url = reverse_lazy('questionarios:trafego_originado_list')
    permission_required = 'questionarios.change_trafegooriginadoindicador'

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        messages.success(self.request, 'Indicador atualizado com sucesso!')
        return super().form_valid(form)

class TrafegoOriginadoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TrafegoOriginadoIndicador
    template_name = 'questionarios/trafego_originado_confirm_delete.html'
    success_url = reverse_lazy('questionarios:trafego_originado_list')
    permission_required = 'questionarios.delete_trafegooriginadoindicador'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Indicador excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

class TrafegoOriginadoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TrafegoOriginadoIndicador
    template_name = 'questionarios/trafego_originado_detail.html'
    context_object_name = 'indicador'
    permission_required = 'questionarios.view_trafegooriginadoindicador'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        
        # Adicionar cálculos e formatações
        context['totals'] = {
            'dados': {
                '2g_mb': obj.calcular_total_dados_2g_mb(),
                '3g_mb': obj.calcular_total_dados_3g_mb(),
                '4g_mb': obj.calcular_total_dados_4g_mb(),
                'total_mb': obj.calcular_total_dados_mb(),
                'total_gb': obj.calcular_total_dados_gb(),
                'total_sessoes': obj.calcular_total_sessoes()
            },
            'sms': {
                'nacional': obj.calcular_total_sms_nacional(),
                'internacional': obj.calcular_total_sms_internacional(),
                'total': obj.calcular_total_sms()
            },
            'voz': {
                'nacional_minutos': obj.calcular_total_voz_nacional_minutos(),
                'internacional_minutos': obj.calcular_total_voz_internacional_minutos(),
                'total_minutos': obj.calcular_total_voz_minutos(),
                'on_net_percent': obj.get_percentual_on_net(),
                'internacional_percent': obj.get_percentual_internacional()
            },
            'chamadas': {
                'nacional': obj.calcular_total_chamadas_nacional(),
                'internacional': obj.calcular_total_chamadas_internacional(),
                'total': obj.calcular_total_chamadas()
            }
        }
        
        # Validações
        context['validation_errors'] = obj.validar_consistencia()
        
        # Calcular duração média das chamadas
        if obj.chamadas_total > 0:
            context['duracao_media_chamada'] = obj.voz_total_minutos / obj.chamadas_total
        else:
            context['duracao_media_chamada'] = 0
        
        return context

class TrafegoOriginadoResumoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TrafegoOriginadoIndicador
    template_name = 'questionarios/trafego_originado_resumo.html'
    context_object_name = 'indicadores'
    permission_required = 'questionarios.view_trafegooriginadoindicador'

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
        
        # Mapeamento trimestre-meses
        trimestre_meses = {
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }
        
        # Cálculos trimestrais usando agregação
        totais_trimestrais = []
        
        for trimestre, meses in trimestre_meses.items():
            dados_trimestre = indicadores.filter(mes__in=meses)
            
            if dados_trimestre.exists():
                # Usar agregação para performance
                totais = dados_trimestre.aggregate(
                    # Dados 2G
                    total_dados_2g_mb=Coalesce(
                        Sum('trafego_dados_2g_mbytes'), 0
                    ),
                    total_sessoes_2g=Coalesce(
                        Sum('trafego_dados_2g_sessoes'), 0
                    ),
                    
                    # Dados 3G
                    total_dados_3g_mb=Coalesce(
                        Sum(F('trafego_dados_3g_upgrade_mbytes') +
                            F('internet_3g_mbytes') +
                            F('internet_3g_placas_modem_mbytes') +
                            F('internet_3g_modem_usb_mbytes')),
                        0
                    ),
                    total_sessoes_3g=Coalesce(
                        Sum(F('trafego_dados_3g_upgrade_sessoes') +
                            F('internet_3g_sessoes') +
                            F('internet_3g_placas_modem_sessoes') +
                            F('internet_3g_modem_usb_sessoes')),
                        0
                    ),
                    
                    # Dados 4G
                    total_dados_4g_mb=Coalesce(
                        Sum(F('trafego_dados_4g_mbytes') +
                            F('internet_4g_mbytes') +
                            F('internet_4g_placas_modem_mbytes') +
                            F('internet_4g_modem_usb_mbytes')),
                        0
                    ),
                    total_sessoes_4g=Coalesce(
                        Sum(F('trafego_dados_4g_sessoes') +
                            F('internet_4g_sessoes') +
                            F('internet_4g_placas_modem_sessoes') +
                            F('internet_4g_modem_usb_sessoes')),
                        0
                    ),
                    
                    # SMS
                    total_sms=Coalesce(Sum('sms_total'), 0),
                    total_sms_on_net=Coalesce(Sum('sms_on_net'), 0),
                    total_sms_off_net=Coalesce(Sum('sms_off_net_nacional'), 0),
                    total_sms_internacional=Coalesce(Sum('sms_internacional_total'), 0),
                    
                    # Voz
                    total_voz_minutos=Coalesce(Sum('voz_total_minutos'), 0),
                    total_voz_on_net=Coalesce(Sum('voz_on_net_minutos'), 0),
                    total_voz_off_net=Coalesce(Sum('voz_off_net_nacional_minutos'), 0),
                    total_voz_internacional=Coalesce(Sum('voz_internacional_total_minutos'), 0),
                    
                    # Chamadas
                    total_chamadas=Coalesce(Sum('chamadas_total'), 0),
                    total_chamadas_on_net=Coalesce(Sum('chamadas_on_net'), 0),
                    total_chamadas_off_net=Coalesce(Sum('chamadas_off_net_nacional'), 0),
                    total_chamadas_internacional=Coalesce(Sum('chamadas_internacional_total'), 0),
                    
                    # Outros
                    total_mms=Coalesce(Sum('mms_total'), 0),
                    total_numeros_curtos=Coalesce(Sum('numeros_curtos'), 0)
                )
                
                # Calcular totais de dados
                totais['total_dados_mb'] = (
                    totais['total_dados_2g_mb'] +
                    totais['total_dados_3g_mb'] +
                    totais['total_dados_4g_mb']
                )
                totais['total_dados_gb'] = totais['total_dados_mb'] / 1024
                
                totais['total_sessoes'] = (
                    totais['total_sessoes_2g'] +
                    totais['total_sessoes_3g'] +
                    totais['total_sessoes_4g']
                )
                
                # Calcular percentuais
                if totais['total_voz_minutos'] > 0:
                    totais['percentual_on_net'] = (
                        totais['total_voz_on_net'] / totais['total_voz_minutos'] * 100
                    )
                    totais['percentual_internacional'] = (
                        totais['total_voz_internacional'] / totais['total_voz_minutos'] * 100
                    )
                else:
                    totais['percentual_on_net'] = 0
                    totais['percentual_internacional'] = 0
                
                # Duração média das chamadas
                if totais['total_chamadas'] > 0:
                    totais['duracao_media'] = totais['total_voz_minutos'] / totais['total_chamadas']
                else:
                    totais['duracao_media'] = 0
                
                totais['trimestre'] = trimestre
                totais['tem_dados'] = True
                
            else:
                # Trimestre sem dados
                totais = {
                    'trimestre': trimestre,
                    'tem_dados': False,
                    'total_dados_mb': 0,
                    'total_dados_gb': 0,
                    'total_sms': 0,
                    'total_voz_minutos': 0,
                    'total_chamadas': 0
                }
            
            totais_trimestrais.append(totais)
        
        # Cálculos anuais usando agregação
        if indicadores.exists():
            totais_anuais = indicadores.aggregate(
                # Dados totais
                total_dados_2g_anual=Coalesce(Sum('trafego_dados_2g_mbytes'), 0),
                total_dados_3g_anual=Coalesce(
                    Sum(F('trafego_dados_3g_upgrade_mbytes') +
                        F('internet_3g_mbytes') +
                        F('internet_3g_placas_modem_mbytes') +
                        F('internet_3g_modem_usb_mbytes')),
                    0
                ),
                total_dados_4g_anual=Coalesce(
                    Sum(F('trafego_dados_4g_mbytes') +
                        F('internet_4g_mbytes') +
                        F('internet_4g_placas_modem_mbytes') +
                        F('internet_4g_modem_usb_mbytes')),
                    0
                ),
                
                # SMS
                total_sms_anual=Coalesce(Sum('sms_total'), 0),
                total_sms_on_net_anual=Coalesce(Sum('sms_on_net'), 0),
                total_sms_internacional_anual=Coalesce(Sum('sms_internacional_total'), 0),
                
                # Voz
                total_voz_minutos_anual=Coalesce(Sum('voz_total_minutos'), 0),
                total_voz_on_net_anual=Coalesce(Sum('voz_on_net_minutos'), 0),
                total_voz_internacional_anual=Coalesce(Sum('voz_internacional_total_minutos'), 0),
                
                # Chamadas
                total_chamadas_anual=Coalesce(Sum('chamadas_total'), 0),
                total_chamadas_on_net_anual=Coalesce(Sum('chamadas_on_net'), 0),
                total_chamadas_internacional_anual=Coalesce(Sum('chamadas_internacional_total'), 0),
                
                # Sessões
                total_sessoes_anual=Coalesce(
                    Sum(F('trafego_dados_2g_sessoes') +
                        F('trafego_dados_3g_upgrade_sessoes') +
                        F('trafego_dados_4g_sessoes')),
                    0
                )
            )
            
            # Calcular total de dados
            totais_anuais['total_dados_mb_anual'] = (
                totais_anuais['total_dados_2g_anual'] +
                totais_anuais['total_dados_3g_anual'] +
                totais_anuais['total_dados_4g_anual']
            )
            totais_anuais['total_dados_gb_anual'] = totais_anuais['total_dados_mb_anual'] / 1024
            totais_anuais['total_dados_tb_anual'] = totais_anuais['total_dados_gb_anual'] / 1024
            
            # Percentuais anuais
            if totais_anuais['total_voz_minutos_anual'] > 0:
                totais_anuais['percentual_on_net_anual'] = (
                    totais_anuais['total_voz_on_net_anual'] / 
                    totais_anuais['total_voz_minutos_anual'] * 100
                )
                totais_anuais['percentual_internacional_anual'] = (
                    totais_anuais['total_voz_internacional_anual'] / 
                    totais_anuais['total_voz_minutos_anual'] * 100
                )
            
        else:
            # Sem dados no ano
            totais_anuais = {
                'total_dados_mb_anual': 0,
                'total_dados_gb_anual': 0,
                'total_dados_tb_anual': 0,
                'total_sms_anual': 0,
                'total_voz_minutos_anual': 0,
                'total_chamadas_anual': 0,
                'total_sessoes_anual': 0
            }
        
        # Adicionar ao contexto
        context['ano'] = ano
        context['operadora_selecionada'] = operadora
        context['totais_trimestrais'] = totais_trimestrais
        
        # Adicionar totais anuais
        for key, value in totais_anuais.items():
            context[key] = value
        
        # Estatísticas adicionais
        context['num_meses_com_dados'] = indicadores.count()
        context['operadoras_disponiveis'] = ['ORANGE', 'TELECEL']
        
        # Comparação entre operadoras se não houver filtro
        if not operadora:
            orange_data = indicadores.filter(operadora='ORANGE').aggregate(
                total_voz=Coalesce(Sum('voz_total_minutos'), 0),
                total_sms=Coalesce(Sum('sms_total'), 0)
            )
            telecel_data = indicadores.filter(operadora='TELECEL').aggregate(
                total_voz=Coalesce(Sum('voz_total_minutos'), 0),
                total_sms=Coalesce(Sum('sms_total'), 0)
            )
            
            context['comparacao_operadoras'] = {
                'orange': orange_data,
                'telecel': telecel_data
            }
        
        return context