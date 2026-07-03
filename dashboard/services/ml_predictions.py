"""
Serviço de Previsões com Machine Learning - ARN
Análise preditiva de tendências do mercado de telecomunicações
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Avg, Count, F
from django.utils import timezone

from questionarios.models import (
    AssinantesIndicador,
    ReceitasIndicador,
    TrafegoOriginadoIndicador,
    EstacoesMoveisIndicador
)


class ARNPredictionService:
    """
    Serviço de previsões usando Machine Learning
    Implementa modelos simples e eficazes sem dependências pesadas
    """
    
    def __init__(self, year=None):
        self.current_year = year or timezone.now().year
    
    # ===== PREVISÃO DE CRESCIMENTO DE ASSINANTES =====
    
    def predict_subscriber_growth(self, months_ahead=6, operator=None):
        """
        Prevê crescimento de assinantes usando regressão linear simples
        
        Args:
            months_ahead: Número de meses para prever
            operator: Operadora específica ou None para todas
        
        Returns:
            dict com previsões e métricas
        """
        # Obter dados históricos (últimos 24 meses)
        historical_data = self._get_subscriber_historical_data(24, operator)
        
        if not historical_data:
            return {
                'error': 'Dados históricos insuficientes',
                'predictions': []
            }
        
        # Preparar dados para modelo
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = np.array([d['total'] for d in historical_data])
        
        # Calcular regressão linear manualmente (sem sklearn)
        n = len(X)
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        # Coeficientes da regressão
        numerator = np.sum((X.flatten() - x_mean) * (y - y_mean))
        denominator = np.sum((X.flatten() - x_mean) ** 2)
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Fazer previsões
        predictions = []
        last_month_index = len(historical_data) - 1
        
        for i in range(1, months_ahead + 1):
            future_index = last_month_index + i
            predicted_value = slope * future_index + intercept
            
            # Calcular intervalo de confiança (±10%)
            confidence_interval = predicted_value * 0.1
            
            predictions.append({
                'month_offset': i,
                'predicted_subscribers': int(max(0, predicted_value)),
                'lower_bound': int(max(0, predicted_value - confidence_interval)),
                'upper_bound': int(predicted_value + confidence_interval),
                'confidence': 'medium' if i <= 3 else 'low'
            })
        
        # Calcular métricas
        growth_rate = ((predictions[-1]['predicted_subscribers'] - y[-1]) / y[-1] * 100) if y[-1] > 0 else 0
        
        return {
            'predictions': predictions,
            'current_subscribers': int(y[-1]),
            'historical_trend': 'growing' if slope > 0 else 'declining',
            'projected_growth_rate': round(growth_rate, 2),
            'confidence_score': self._calculate_confidence_score(y, slope, intercept),
            'model': 'linear_regression'
        }
    
    def _get_subscriber_historical_data(self, months_back=24, operator=None):
        """Obtém dados históricos de assinantes"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        queryset = AssinantesIndicador.objects.filter(
            ano__gte=start_date.year - 1,
            ano__lte=end_date.year
        )
        
        if operator:
            queryset = queryset.filter(operadora=operator)
        
        # Agrupar por mês
        monthly_data = []
        for year in range(start_date.year, end_date.year + 1):
            for month in range(1, 13):
                if (year == start_date.year and month < start_date.month) or \
                   (year == end_date.year and month > end_date.month):
                    continue
                
                month_data = queryset.filter(ano=year, mes=month)
                total = month_data.aggregate(
                    total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
                )['total'] or 0
                
                if total > 0:
                    monthly_data.append({
                        'year': year,
                        'month': month,
                        'total': total
                    })
        
        return monthly_data[-months_back:] if len(monthly_data) > months_back else monthly_data
    
    def _calculate_confidence_score(self, y, slope, intercept):
        """Calcula score de confiança da previsão"""
        # Calcular R² (coeficiente de determinação)
        y_pred = slope * np.arange(len(y)) + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Converter para score 0-100
        confidence = max(0, min(100, r_squared * 100))
        return round(confidence, 2)
    
    # ===== PREVISÃO DE RECEITAS =====
    
    def predict_revenue_trends(self, months_ahead=6, operator=None):
        """
        Prevê tendências de receita
        """
        # Obter dados históricos de receitas
        historical_data = self._get_revenue_historical_data(24, operator)
        
        if not historical_data:
            return {
                'error': 'Dados históricos insuficientes',
                'predictions': []
            }
        
        # Preparar dados
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = np.array([d['total'] for d in historical_data])
        
        # Regressão linear
        n = len(X)
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X.flatten() - x_mean) * (y - y_mean))
        denominator = np.sum((X.flatten() - x_mean) ** 2)
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Previsões
        predictions = []
        last_month_index = len(historical_data) - 1
        
        for i in range(1, months_ahead + 1):
            future_index = last_month_index + i
            predicted_value = slope * future_index + intercept
            
            predictions.append({
                'month_offset': i,
                'predicted_revenue': float(max(0, predicted_value)),
                'formatted': f"{predicted_value:,.0f} FCFA" if predicted_value > 0 else "0 FCFA"
            })
        
        # Calcular crescimento esperado
        growth_rate = ((predictions[-1]['predicted_revenue'] - y[-1]) / y[-1] * 100) if y[-1] > 0 else 0
        
        return {
            'predictions': predictions,
            'current_revenue': float(y[-1]),
            'projected_growth_rate': round(growth_rate, 2),
            'trend': 'increasing' if slope > 0 else 'decreasing',
            'confidence_score': self._calculate_confidence_score(y, slope, intercept)
        }
    
    def _get_revenue_historical_data(self, months_back=24, operator=None):
        """Obtém dados históricos de receitas"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        queryset = ReceitasIndicador.objects.filter(
            ano__gte=start_date.year - 1,
            ano__lte=end_date.year
        )
        
        if operator:
            queryset = queryset.filter(operadora=operator)
        
        monthly_data = []
        for year in range(start_date.year, end_date.year + 1):
            for month in range(1, 13):
                if (year == start_date.year and month < start_date.month) or \
                   (year == end_date.year and month > end_date.month):
                    continue
                
                month_data = queryset.filter(ano=year, mes=month)
                
                # Calcular receita total (soma de todos os campos)
                total = month_data.aggregate(
                    total=Sum(
                        F('receitas_mensalidades') +
                        F('receitas_chamadas_on_net') +
                        F('receitas_chamadas_off_net') +
                        F('receitas_dados_moveis') +
                        F('receitas_internet_banda_larga') +
                        F('outras_receitas_retalhistas') +
                        F('receitas_terminacao_voz') +
                        F('outras_receitas_grossistas')
                    )
                )['total'] or 0
                
                if total > 0:
                    monthly_data.append({
                        'year': year,
                        'month': month,
                        'total': float(total)
                    })
        
        return monthly_data[-months_back:] if len(monthly_data) > months_back else monthly_data
    
    # ===== ANÁLISE DE SATURAÇÃO DE MERCADO =====
    
    def calculate_market_saturation(self, operator=None):
        """
        Calcula o nível de saturação do mercado
        
        Returns:
            dict com métricas de saturação
        """
        # População estimada da Guiné-Bissau
        POPULATION = 2000000
        
        # Obter assinantes atuais
        current_year = self.current_year
        current_data = AssinantesIndicador.objects.filter(ano=current_year)
        
        if operator:
            current_data = current_data.filter(operadora=operator)
        
        total_subscribers = current_data.aggregate(
            total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
        )['total'] or 0
        
        # Calcular taxa de penetração
        penetration_rate = (total_subscribers / POPULATION) * 100 if POPULATION > 0 else 0
        
        # Estimar saturação (considerando que >100% é possível - múltiplos SIMs)
        # Saturação ideal: 80-120%
        if penetration_rate < 50:
            saturation_level = 'low'
            growth_potential = 'high'
        elif penetration_rate < 80:
            saturation_level = 'medium'
            growth_potential = 'medium'
        elif penetration_rate < 120:
            saturation_level = 'high'
            growth_potential = 'low'
        else:
            saturation_level = 'very_high'
            growth_potential = 'very_low'
        
        # Estimar mercado potencial restante
        potential_market = max(0, POPULATION * 1.2 - total_subscribers)  # Assumindo max 120%
        
        return {
            'penetration_rate': round(penetration_rate, 2),
            'total_subscribers': total_subscribers,
            'population': POPULATION,
            'saturation_level': saturation_level,
            'growth_potential': growth_potential,
            'potential_market': int(potential_market),
            'market_maturity': self._classify_market_maturity(penetration_rate)
        }
    
    def _classify_market_maturity(self, penetration_rate):
        """Classifica maturidade do mercado"""
        if penetration_rate < 30:
            return 'emerging'
        elif penetration_rate < 60:
            return 'developing'
        elif penetration_rate < 90:
            return 'mature'
        else:
            return 'saturated'
    
    # ===== PREVISÃO DE TRÁFEGO DE DADOS =====
    
    def predict_data_traffic_growth(self, months_ahead=6):
        """
        Prevê crescimento de tráfego de dados móveis
        """
        # Obter dados históricos de tráfego
        historical_data = self._get_traffic_historical_data(24)
        
        if not historical_data:
            return {
                'error': 'Dados históricos insuficientes',
                'predictions': []
            }
        
        # Preparar dados
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = np.array([d['total_mb'] for d in historical_data])
        
        # Regressão linear
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X.flatten() - x_mean) * (y - y_mean))
        denominator = np.sum((X.flatten() - x_mean) ** 2)
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Previsões
        predictions = []
        last_month_index = len(historical_data) - 1
        
        for i in range(1, months_ahead + 1):
            future_index = last_month_index + i
            predicted_mb = slope * future_index + intercept
            predicted_gb = predicted_mb / 1024
            
            predictions.append({
                'month_offset': i,
                'predicted_traffic_mb': int(max(0, predicted_mb)),
                'predicted_traffic_gb': round(max(0, predicted_gb), 2)
            })
        
        # Calcular crescimento
        growth_rate = ((predictions[-1]['predicted_traffic_mb'] - y[-1]) / y[-1] * 100) if y[-1] > 0 else 0
        
        return {
            'predictions': predictions,
            'current_traffic_gb': round(y[-1] / 1024, 2),
            'projected_growth_rate': round(growth_rate, 2),
            'trend': 'increasing' if slope > 0 else 'stable',
            'avg_monthly_growth': round(slope / 1024, 2)  # GB por mês
        }
    
    def _get_traffic_historical_data(self, months_back=24):
        """Obtém dados históricos de tráfego de dados"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        queryset = TrafegoOriginadoIndicador.objects.filter(
            ano__gte=start_date.year - 1,
            ano__lte=end_date.year
        )
        
        monthly_data = []
        for year in range(start_date.year, end_date.year + 1):
            for month in range(1, 13):
                if (year == start_date.year and month < start_date.month) or \
                   (year == end_date.year and month > end_date.month):
                    continue
                
                month_data = queryset.filter(ano=year, mes=month)
                
                # Somar tráfego de dados de todas as tecnologias
                total_mb = month_data.aggregate(
                    total=Sum(
                        F('trafego_dados_2g_mbytes') +
                        F('trafego_dados_3g_upgrade_mbytes') +
                        F('trafego_dados_4g_mbytes')
                    )
                )['total'] or 0
                
                if total_mb > 0:
                    monthly_data.append({
                        'year': year,
                        'month': month,
                        'total_mb': total_mb
                    })
        
        return monthly_data[-months_back:] if len(monthly_data) > months_back else monthly_data
    
    # ===== INSIGHTS AUTOMÁTICOS =====
    
    def generate_market_insights(self):
        """
        Gera insights automáticos baseados em análises
        """
        insights = []
        
        # Insight 1: Crescimento de assinantes
        subscriber_prediction = self.predict_subscriber_growth(months_ahead=3)
        if not subscriber_prediction.get('error'):
            if subscriber_prediction['projected_growth_rate'] > 5:
                insights.append({
                    'type': 'positive',
                    'category': 'subscribers',
                    'title': 'Crescimento Forte de Assinantes',
                    'message': f"Projeção de crescimento de {subscriber_prediction['projected_growth_rate']:.1f}% nos próximos 3 meses",
                    'priority': 'high'
                })
            elif subscriber_prediction['projected_growth_rate'] < -5:
                insights.append({
                    'type': 'warning',
                    'category': 'subscribers',
                    'title': 'Declínio de Assinantes',
                    'message': f"Atenção: Projeção indica queda de {abs(subscriber_prediction['projected_growth_rate']):.1f}%",
                    'priority': 'high'
                })
        
        # Insight 2: Saturação de mercado
        saturation = self.calculate_market_saturation()
        if saturation['saturation_level'] == 'high' or saturation['saturation_level'] == 'very_high':
            insights.append({
                'type': 'info',
                'category': 'market',
                'title': 'Mercado em Saturação',
                'message': f"Taxa de penetração de {saturation['penetration_rate']:.1f}% indica mercado maduro",
                'priority': 'medium'
            })
        
        # Insight 3: Tráfego de dados
        traffic_prediction = self.predict_data_traffic_growth(months_ahead=3)
        if not traffic_prediction.get('error'):
            if traffic_prediction['projected_growth_rate'] > 20:
                insights.append({
                    'type': 'positive',
                    'category': 'traffic',
                    'title': 'Explosão de Tráfego de Dados',
                    'message': f"Tráfego de dados crescendo {traffic_prediction['projected_growth_rate']:.1f}% - oportunidade para pacotes de dados",
                    'priority': 'high'
                })
        
        # Insight 4: Receitas
        revenue_prediction = self.predict_revenue_trends(months_ahead=3)
        if not revenue_prediction.get('error'):
            if revenue_prediction['trend'] == 'decreasing':
                insights.append({
                    'type': 'warning',
                    'category': 'revenue',
                    'title': 'Tendência de Queda em Receitas',
                    'message': 'Receitas projetadas em declínio - revisar estratégia de preços',
                    'priority': 'high'
                })
        
        return insights

