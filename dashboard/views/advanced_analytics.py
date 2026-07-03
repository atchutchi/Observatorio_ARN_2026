"""
Views para Análises Avançadas - ARN
Dashboards com ML, Análise Geográfica e Preços
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.utils import timezone

from ..services.ml_predictions import ARNPredictionService
from ..services.geographic_analytics import GeographicAnalyticsService
from ..services.price_analysis import PriceAnalysisService


# ===== DASHBOARD DE PREVISÕES =====

class PredictionsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard de Previsões com Machine Learning"""
    template_name = 'dashboard/advanced/predictions.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        months_ahead = int(self.request.GET.get('months', 6))
        
        # Inicializar serviço de previsões
        ml_service = ARNPredictionService(year=year)
        
        # Obter previsões
        context.update({
            'year': year,
            'months_ahead': months_ahead,
            'subscriber_forecast': ml_service.predict_subscriber_growth(months_ahead),
            'revenue_forecast': ml_service.predict_revenue_trends(months_ahead),
            'traffic_forecast': ml_service.predict_data_traffic_growth(months_ahead),
            'market_saturation': ml_service.calculate_market_saturation(),
            'insights': ml_service.generate_market_insights()
        })
        
        return context


class PredictionsAPIView(LoginRequiredMixin, View):
    """API para obter previsões em JSON"""
    
    def get(self, request):
        year = int(request.GET.get('year', timezone.now().year))
        months = int(request.GET.get('months', 6))
        prediction_type = request.GET.get('type', 'subscribers')
        operator = request.GET.get('operator', None)
        
        ml_service = ARNPredictionService(year=year)
        
        if prediction_type == 'subscribers':
            data = ml_service.predict_subscriber_growth(months, operator)
        elif prediction_type == 'revenue':
            data = ml_service.predict_revenue_trends(months, operator)
        elif prediction_type == 'traffic':
            data = ml_service.predict_data_traffic_growth(months)
        elif prediction_type == 'saturation':
            data = ml_service.calculate_market_saturation(operator)
        elif prediction_type == 'insights':
            data = {'insights': ml_service.generate_market_insights()}
        else:
            data = {'error': 'Tipo de previsão inválido'}
        
        return JsonResponse(data, safe=False)


# ===== ANÁLISE GEOGRÁFICA =====

class GeographicAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard de Análise Geográfica"""
    template_name = 'dashboard/advanced/geographic.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        operator = self.request.GET.get('operator', None)
        
        # Inicializar serviço geográfico
        geo_service = GeographicAnalyticsService(year=year)
        
        # Obter análises
        context.update({
            'year': year,
            'operator': operator,
            'coverage_map': geo_service.generate_coverage_map(operator),
            'penetration_data': geo_service.analyze_regional_penetration(operator),
            'underserved_areas': geo_service.identify_underserved_areas(),
            'urban_rural_comparison': geo_service.compare_urban_rural(),
            'insights': geo_service.generate_geographic_insights()
        })
        
        return context


class GeographicAPIView(LoginRequiredMixin, View):
    """API para dados geográficos"""
    
    def get(self, request):
        year = int(request.GET.get('year', timezone.now().year))
        analysis_type = request.GET.get('type', 'coverage')
        operator = request.GET.get('operator', None)
        
        geo_service = GeographicAnalyticsService(year=year)
        
        if analysis_type == 'coverage':
            data = geo_service.generate_coverage_map(operator)
        elif analysis_type == 'penetration':
            data = geo_service.analyze_regional_penetration(operator)
        elif analysis_type == 'underserved':
            data = {'underserved_areas': geo_service.identify_underserved_areas()}
        elif analysis_type == 'comparison':
            data = geo_service.compare_urban_rural()
        elif analysis_type == 'insights':
            data = {'insights': geo_service.generate_geographic_insights()}
        else:
            data = {'error': 'Tipo de análise inválido'}
        
        return JsonResponse(data, safe=False)


# ===== ANÁLISE DE PREÇOS =====

class PriceAnalyticsView(LoginRequiredMixin, TemplateView):
    """Dashboard de Análise de Preços (Público)"""
    template_name = 'dashboard/advanced/prices.html'
    
    # Não requer staff - acessível a todos
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        
        # Inicializar serviço de preços
        price_service = PriceAnalysisService(year=year)
        
        # Obter análises
        context.update({
            'year': year,
            'price_comparison': price_service.compare_operator_prices(),
            'best_deals': price_service.identify_best_deals(),
            'price_index': price_service.calculate_price_index(),
            'price_evolution': price_service.analyze_price_evolution(years_back=3),
            'public_comparison': price_service.get_public_price_comparison(),
            'insights': price_service.generate_price_insights()
        })
        
        return context


class PriceAPIView(View):
    """API pública para comparação de preços"""
    
    def get(self, request):
        year = int(request.GET.get('year', timezone.now().year))
        analysis_type = request.GET.get('type', 'comparison')
        
        price_service = PriceAnalysisService(year=year)
        
        if analysis_type == 'comparison':
            data = price_service.compare_operator_prices()
        elif analysis_type == 'best_deals':
            data = price_service.identify_best_deals()
        elif analysis_type == 'index':
            data = price_service.calculate_price_index()
        elif analysis_type == 'evolution':
            years_back = int(request.GET.get('years', 3))
            data = price_service.analyze_price_evolution(years_back)
        elif analysis_type == 'public':
            data = price_service.get_public_price_comparison()
        elif analysis_type == 'insights':
            data = {'insights': price_service.generate_price_insights()}
        else:
            data = {'error': 'Tipo de análise inválido'}
        
        return JsonResponse(data, safe=False)


# ===== DASHBOARD CONSOLIDADO =====

class AdvancedAnalyticsDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard consolidado com todas as análises avançadas"""
    template_name = 'dashboard/advanced/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        
        # Inicializar todos os serviços
        ml_service = ARNPredictionService(year=year)
        geo_service = GeographicAnalyticsService(year=year)
        price_service = PriceAnalysisService(year=year)
        
        # Consolidar insights de todos os serviços
        all_insights = []
        all_insights.extend(ml_service.generate_market_insights())
        all_insights.extend(geo_service.generate_geographic_insights())
        all_insights.extend(price_service.generate_price_insights())
        
        # Ordenar por prioridade
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        all_insights.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        # KPIs principais
        market_saturation = ml_service.calculate_market_saturation()
        subscriber_forecast = ml_service.predict_subscriber_growth(months_ahead=3)
        
        context.update({
            'year': year,
            'insights': all_insights,
            'kpis': {
                'penetration_rate': market_saturation.get('penetration_rate', 0),
                'market_maturity': market_saturation.get('market_maturity', 'unknown'),
                'growth_projection': subscriber_forecast.get('projected_growth_rate', 0) if not subscriber_forecast.get('error') else 0,
                'trend': subscriber_forecast.get('historical_trend', 'stable') if not subscriber_forecast.get('error') else 'unknown'
            },
            'has_predictions': True,
            'has_geographic': True,
            'has_pricing': True
        })
        
        return context

