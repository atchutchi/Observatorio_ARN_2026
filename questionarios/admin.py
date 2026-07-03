# admin.py
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.utils import timezone
import logging
from .models import (
    RegistroQuestionario, 
    AssinantesIndicador, 
    ReceitasIndicador,
    TrafegoOriginadoIndicador,
    TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador,
    LBIIndicador,
    TrafegoInternetIndicador,
    InternetFixoIndicador,
    EstacoesMoveisIndicador,
    InvestimentoIndicador,
    TarifarioVozOrangeIndicador,
    TarifarioVozMTNIndicador,
    EmpregoIndicador
)

logger = logging.getLogger(__name__)

@admin.register(EstacoesMoveisIndicador)
class EstacoesMoveisIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar EstacoesMoveisIndicador: {e}")
            raise

@admin.register(TrafegoOriginadoIndicador)
class TrafegoOriginadoIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar TrafegoOriginadoIndicador: {e}")
            raise

@admin.register(TrafegoTerminadoIndicador)
class TrafegoTerminadoIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar TrafegoTerminadoIndicador: {e}")
            raise

@admin.register(TrafegoRoamingInternacionalIndicador)
class TrafegoRoamingInternacionalIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar TrafegoRoamingInternacionalIndicador: {e}")
            raise

@admin.register(LBIIndicador)
class LBIIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar LBIIndicador: {e}")
            raise

@admin.register(TrafegoInternetIndicador)
class TrafegoInternetIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'trafego_total', 'banda_larga_total', 'criado_por', 'data_criacao']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Tráfego de Serviços de Internet fixo via rádio', {
            'fields': ('trafego_total', 'por_via_satelite', 'por_sistema_hertziano_fixo_terra', 'fibra_otica')
        }),
        ('Tráfego por débito', {
            'fields': ('banda_estreita_256kbps', 'kbps_64_128', 'kbps_128_256', 'banda_estreita_outros')
        }),
        ('Banda Larga ≥ 256 Kbps', {
            'fields': ('banda_larga_total', 'kbits_256_2mbits', 'mbits_2_4', 'mbits_10', 'banda_larga_outros')
        }),
        ('Tráfego por categoria', {
            'fields': ('residencial', 'corporativo_empresarial', 'instituicoes_publicas', 'instituicoes_ensino', 'instituicoes_saude', 'ong_outros')
        }),
        ('Tráfego por Região', {
            'fields': ('cidade_bissau', 'bafata', 'biombo', 'bolama_bijagos', 'cacheu', 'gabu', 'oio', 'quinara', 'tombali')
        }),
        ('Tráfego por acesso público via rádio (PWLAN)', {
            'fields': ('acesso_livre', 'acesso_condicionado')
        }),
        ('Metadados', {
            'fields': ('criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar TrafegoInternetIndicador: {e}")
            raise

@admin.register(InternetFixoIndicador)
class InternetFixoIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'cidade_bissau', 'bafata', 'biombo']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes', 'cidade_bissau', 'bafata', 'biombo']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Número de assinantes de Internet fixo via rádio', {
            'fields': ('cidade_bissau', 'bafata', 'biombo', 'bolama_bijagos', 'cacheu', 'gabu', 'oio', 'quinara', 'tombali')
        }),
        ('Número de assinantes activos de Internet Fixo via Rádio', {
            'fields': ('airbox', 'sistema_hertziano_fixo_terra', 'outros_proxim', 'fibra_otica')
        }),
        ('Número de assinantes de Serviços de Internet por débito', {
            'fields': ('banda_larga_256kbits_2mbits', 'banda_larga_2_4mbits', 'banda_larga_5_10mbits', 'banda_larga_outros')
        }),
        ('Número de assinantes de Internet por categoria', {
            'fields': ('residencial', 'corporativo_empresarial', 'instituicoes_publicas', 'instituicoes_ensino', 'instituicoes_saude', 'ong_outros')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar InternetFixoIndicador: {e}")
            raise

@admin.register(ReceitasIndicador)
class ReceitasIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Receitas de serviços a clientes retalhistas', {
            'fields': ('receitas_mensalidades',)
        }),
        ('Receitas de serviços de voz', {
            'fields': (
                'receitas_chamadas_on_net',
                'receitas_chamadas_off_net',
                'receitas_chamadas_telecel',
                'receitas_chamadas_rede_movel_b',
                'receitas_chamadas_outros',
                'receitas_servico_telefonico_fixo'
            )
        }),
        ('Receitas de chamadas internacionais', {
            'fields': (
                'receitas_chamadas_cedeao',
                'receitas_chamadas_cplp',
                'receitas_chamadas_palop',
                'receitas_chamadas_resto_africa',
                'receitas_chamadas_resto_mundo'
            )
        }),
        ('Receitas de Roaming e Mensagens', {
            'fields': (
                'receitas_voz_roaming_out',
                'receitas_mensagens',
                'receitas_mms'
            )
        }),
        ('Receitas de Dados Móveis', {
            'fields': (
                'receitas_dados_moveis',
                'receitas_internet_banda_larga',
                'receitas_videochamadas',
                'receitas_mobile_tv',
                'receitas_outros_servicos_dados'
            )
        }),
        ('Receitas de Roaming-out (excluindo voz)', {
            'fields': (
                'receitas_roaming_out_dados',
                'receitas_internet_roaming_out'
            )
        }),
        ('Outras Receitas Retalhistas', {
            'fields': ('outras_receitas_retalhistas',)
        }),
        ('Receitas de serviços a clientes grossistas', {
            'fields': (
                'receitas_terminacao_voz',
                'receitas_terminacao_dados',
                'receitas_originacao_trafego',
                'receitas_servicos_especiais',
                'outras_receitas_grossistas'
            )
        }),
        ('Metadados', {
            'fields': ('criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar ReceitasIndicador: {e}")
            raise

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields


@admin.register(EmpregoIndicador)
class EmpregoIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Emprego Direto', {
            'fields': ('emprego_direto_total',)
        }),
        ('Nacionais', {
            'fields': (
                'nacionais_total',
                'nacionais_homem',
                'nacionais_mulher'
            )
        }),
        ('Emprego Indireto', {
            'fields': ('emprego_indireto',)
        }),
        ('Metadados', {
            'fields': ('criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar EmpregoIndicador: {e}")
            raise

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields


@admin.register(InvestimentoIndicador)
class InvestimentoIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 
                    'calcular_total_corporeo',
                    'calcular_total_incorporeo',
                    'calcular_total_geral']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']

    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Investimento Corpóreo', {
            'fields': (
                'servicos_telecomunicacoes',
                'servicos_internet'
            ),
            'description': 'Investimentos em ativos físicos tangíveis'
        }),
        ('Investimento Incorpóreo', {
            'fields': (
                'servicos_telecomunicacoes_incorporeo',
                'servicos_internet_incorporeo'
            ),
            'description': 'Investimentos em ativos intangíveis'
        }),
        ('Outros Investimentos', {
            'fields': ('outros_investimentos',),
            'description': 'Campos adicionais de investimentos',
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar InvestimentoIndicador: {e}")
            raise

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'outros_investimentos':
            field.widget = forms.Textarea(attrs={'rows': 4})
        return field

@admin.register(TarifarioVozOrangeIndicador)
class TarifarioVozOrangeIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao']
    list_filter = ['ano', 'mes']
    search_fields = ['ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Internet USB Pré-pago', {
            'fields': ('dongle_3g', 'dongle_4g', 'airbox_4g', 'flybox_4g', 'flybox_4g_plus')
        }),
        ('Internet USB/BOX Residencial', {
            'fields': ('casa_zen_2mbits_adesao', 'casa_conforto_4mbits_adesao', 
                      'casabox_2mbits_adesao', 'casabox_5mbits_adesao')
        }),
        ('Subscrição mensal Residencial', {
            'fields': ('casa_zen_2mbits_mensal', 'casa_conforto_4mbits_mensal',
                      'casabox_2mbits_mensal', 'casabox_5mbits_mensal')
        }),
        ('Subscrição mensal por capacidades', {
            'fields': ('pass_ilimite_1h', 'pass_ilimite_3h', 'pass_ilimite_8h', 
                      'pass_ilimite_dimanche', 'pass_ilimite_nuit', 'pass_jours_ferie',
                      'pass_30_mo', 'pass_75_mo', 'pass_150_mo', 'pass_250_mo',
                      'pass_500_mo', 'pass_600_mo', 'pass_1_5_go', 'pass_3_go',
                      'pass_10_go', 'pass_18_go', 'pass_35_go', 'pass_100_go',
                      'pass_400_mo', 'pass_1_go')
        }),
        ('Serviço de Voz', {
            'fields': ('cartao_sim_adesao', 'taxa_adesao')
        }),
        ('Tarifas On-net', {
            'fields': ('tarifa_orange_livre_6h_22h', 'tarifa_orange_livre_22h_6h',
                      'tarifa_orange_jovem_vip_jovem', 'tarifa_orange_jovem_vip_6h_22h',
                      'tarifa_orange_jovem_vip_22h_6h', 'tarifa_orange_intenso')
        }),
        ('Tarifas Off-net (local)', {
            'fields': ('tarifa_offnet_orange_livre', 'tarifa_offnet_orange_jovem_vip',
                      'tarifa_offnet_orange_intenso')
        }),
        ('Tarifas Off-net (Internacional)', {
            'fields': ('tarifa_zona1', 'tarifa_zona2', 'tarifa_zona3',
                      'tarifa_zona4', 'tarifa_zona5', 'tarifa_zona6')
        }),
        ('Outros Serviços', {
            'fields': ('toll_free', 'vpn')
        }),
        ('Informações Adicionais', {
            'fields': ('taxa_imposto', 'promocoes', 'link_plano')
        }),
        ('Metadados', {
            'fields': ('criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar TarifarioVozOrangeIndicador: {e}")
            raise
        
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields
        
@admin.register(TarifarioVozMTNIndicador)
class TarifarioVozMTNIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'criado_por', 'data_criacao']
    list_filter = ['ano', 'mes']
    search_fields = ['ano', 'mes']
    readonly_fields = ['criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Equipamentos', {
            'fields': ('huawei_4g_lte', 'huawei_mobile_wifi_4g')
        }),
        ('Pacotes Diários', {
            'fields': ('pacote_30mb', 'pacote_100mb', 'pacote_300mb', 'pacote_1gb')
        }),
        ('Pacotes Semanais', {
            'fields': ('pacote_650mb', 'pacote_1000mb')
        }),
        ('Pacotes Mensais', {
            'fields': ('pacote_1_5gb', 'pacote_10gb', 'pacote_18gb', 'pacote_30gb',
                      'pacote_50gb', 'pacote_60gb', 'pacote_120gb')
        }),
        ('Pacote Y\'ello Night', {
            'fields': ('pacote_yello_350mb', 'pacote_yello_1_5gb', 'pacote_yello_1_5gb_7dias')
        }),
        ('Pacotes Ilimitados', {
            'fields': ('pacote_1hora', 'pacote_3horas', 'pacote_9horas')
        }),
        ('Informações Adicionais', {
            'fields': ('taxa_imposto', 'link_plano')
        }),
        ('Metadados', {
            'fields': ('criado_por', 'data_criacao', 'atualizado_por', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.criado_por = request.user
            obj.atualizado_por = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar TarifarioVozMTNIndicador: {e}")
            raise
        
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['ano', 'mes', 'operadora']
        return self.readonly_fields

@admin.register(AssinantesIndicador)
class AssinantesIndicadorAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'mes', 'assinantes_pre_pago', 'assinantes_pos_pago', 'assinantes_fixo']
    list_filter = ['operadora', 'ano', 'mes']
    search_fields = ['operadora', 'ano', 'mes']
    readonly_fields = []
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('operadora', 'ano', 'mes')
        }),
        ('Assinantes de telefonia móvel', {
            'fields': ('assinantes_pre_pago', 'assinantes_pos_pago')
        }),
        ('Assinantes de telefonia fixa', {
            'fields': ('assinantes_fixo',)
        }),
        ('Assinantes de internet', {
            'fields': ('assinantes_internet_movel', 'assinantes_internet_fixa')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['ano', 'mes', 'operadora']
        return self.readonly_fields
        
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar AssinantesIndicador: {e}")
            raise

@admin.register(RegistroQuestionario)
class RegistroQuestionarioAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'ano', 'trimestre', 'data_preenchimento', 'usuario']
    list_filter = ['operadora', 'ano', 'trimestre']
    search_fields = ['operadora__nome', 'ano', 'trimestre']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['ano', 'trimestre', 'operadora', 'data_preenchimento', 'usuario']
        return []
        
    def save_model(self, request, obj, form, change):
        try:
            if not change:
                obj.usuario = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            logger.error(f"Erro ao salvar RegistroQuestionario: {e}")
            raise