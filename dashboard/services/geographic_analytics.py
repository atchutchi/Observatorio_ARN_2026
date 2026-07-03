"""
Serviço de Análise Geográfica - ARN
Análise de cobertura e distribuição regional de telecomunicações
"""
from django.db.models import Sum, Avg, Count, F, Q
from decimal import Decimal

from questionarios.models import (
    TrafegoInternetIndicador,
    EstacoesMoveisIndicador,
    AssinantesIndicador
)


class GeographicAnalyticsService:
    """
    Análise geográfica da cobertura de telecomunicações
    Baseado nos dados regionais coletados nos questionários
    """
    
    # Regiões da Guiné-Bissau
    REGIONS = {
        'cidade_bissau': {
            'name': 'Bissau (Cidade)',
            'population_estimate': 492000,
            'type': 'urban'
        },
        'bafata': {
            'name': 'Bafatá',
            'population_estimate': 210000,
            'type': 'rural'
        },
        'biombo': {
            'name': 'Biombo',
            'population_estimate': 97000,
            'type': 'rural'
        },
        'bolama_bijagos': {
            'name': 'Bolama/Bijagós',
            'population_estimate': 34000,
            'type': 'insular'
        },
        'cacheu': {
            'name': 'Cacheu',
            'population_estimate': 192000,
            'type': 'rural'
        },
        'gabu': {
            'name': 'Gabú',
            'population_estimate': 215000,
            'type': 'rural'
        },
        'oio': {
            'name': 'Oio',
            'population_estimate': 224000,
            'type': 'rural'
        },
        'quinara': {
            'name': 'Quinara',
            'population_estimate': 63000,
            'type': 'rural'
        },
        'tombali': {
            'name': 'Tombali',
            'population_estimate': 94000,
            'type': 'rural'
        }
    }
    
    def __init__(self, year=None):
        from django.utils import timezone
        self.year = year or timezone.now().year
    
    # ===== MAPA DE COBERTURA =====
    
    def generate_coverage_map(self, operator=None):
        """
        Gera dados para mapa de cobertura por região
        
        Returns:
            dict com dados de cobertura por região
        """
        coverage_data = {}
        
        # Obter dados de tráfego internet por região
        internet_queryset = TrafegoInternetIndicador.objects.filter(ano=self.year)
        
        if operator:
            internet_queryset = internet_queryset.filter(operadora=operator)
        
        # Agregar dados de internet por região
        for region_code, region_info in self.REGIONS.items():
            # Tráfego de internet na região
            traffic = internet_queryset.aggregate(
                total=Sum(region_code)
            )['total'] or 0
            
            # Calcular nível de cobertura
            coverage_level = self._calculate_coverage_level(
                traffic, 
                region_info['population_estimate']
            )
            
            coverage_data[region_code] = {
                'name': region_info['name'],
                'type': region_info['type'],
                'population': region_info['population_estimate'],
                'traffic_mbps': float(traffic) if traffic else 0,
                'coverage_level': coverage_level,
                'coverage_percentage': self._estimate_coverage_percentage(coverage_level),
                'quality_score': self._calculate_quality_score(traffic, region_info['population_estimate'])
            }
        
        return coverage_data
    
    def _calculate_coverage_level(self, traffic, population):
        """Calcula nível de cobertura baseado em tráfego vs população"""
        if population == 0:
            return 'unknown'
        
        # Tráfego per capita (Mbps por pessoa)
        traffic_per_capita = traffic / population if traffic > 0 else 0
        
        if traffic_per_capita > 0.5:
            return 'excellent'
        elif traffic_per_capita > 0.2:
            return 'good'
        elif traffic_per_capita > 0.05:
            return 'fair'
        elif traffic_per_capita > 0:
            return 'poor'
        else:
            return 'no_coverage'
    
    def _estimate_coverage_percentage(self, coverage_level):
        """Estima percentual de cobertura baseado no nível"""
        coverage_map = {
            'excellent': 95,
            'good': 75,
            'fair': 50,
            'poor': 25,
            'no_coverage': 0,
            'unknown': 0
        }
        return coverage_map.get(coverage_level, 0)
    
    def _calculate_quality_score(self, traffic, population):
        """Calcula score de qualidade (0-100)"""
        if population == 0:
            return 0
        
        traffic_per_capita = traffic / population if traffic > 0 else 0
        
        # Normalizar para score 0-100
        # Assumindo que 1 Mbps per capita = 100
        score = min(100, traffic_per_capita * 100)
        
        return round(score, 2)
    
    # ===== ANÁLISE DE PENETRAÇÃO REGIONAL =====
    
    def analyze_regional_penetration(self, operator=None):
        """
        Analisa taxa de penetração por região
        
        Returns:
            dict com dados de penetração por região
        """
        penetration_data = {}
        
        # Para cada região, calcular penetração
        for region_code, region_info in self.REGIONS.items():
            # Tentar estimar assinantes por região
            # (Nota: AssinantesIndicador não tem dados por região)
            # Usar tráfego como proxy para penetração
            
            internet_data = TrafegoInternetIndicador.objects.filter(
                ano=self.year
            )
            
            if operator:
                internet_data = internet_data.filter(operadora=operator)
            
            regional_traffic = internet_data.aggregate(
                total=Sum(region_code)
            )['total'] or 0
            
            # Calcular penetração estimada
            population = region_info['population_estimate']
            
            # Penetração estimada: (tráfego / população) * fator de ajuste
            # Assumindo que 0.1 Mbps per capita = 50% penetração
            estimated_penetration = min(100, (regional_traffic / population * 500)) if population > 0 else 0
            
            penetration_data[region_code] = {
                'name': region_info['name'],
                'population': population,
                'estimated_penetration': round(estimated_penetration, 2),
                'classification': self._classify_penetration(estimated_penetration),
                'urban_rural': region_info['type']
            }
        
        return penetration_data
    
    def _classify_penetration(self, penetration_rate):
        """Classifica nível de penetração"""
        if penetration_rate > 70:
            return 'high'
        elif penetration_rate > 40:
            return 'medium'
        elif penetration_rate > 15:
            return 'low'
        else:
            return 'very_low'
    
    # ===== IDENTIFICAÇÃO DE ÁREAS CARENTES =====
    
    def identify_underserved_areas(self):
        """
        Identifica regiões com baixa cobertura que precisam de atenção
        
        Returns:
            list de regiões carentes ordenadas por prioridade
        """
        penetration_data = self.analyze_regional_penetration()
        coverage_data = self.generate_coverage_map()
        
        underserved_areas = []
        
        for region_code, region_info in self.REGIONS.items():
            penetration = penetration_data.get(region_code, {})
            coverage = coverage_data.get(region_code, {})
            
            # Calcular score de carência (quanto maior, mais carente)
            underserved_score = self._calculate_underserved_score(
                penetration.get('estimated_penetration', 0),
                coverage.get('coverage_percentage', 0),
                region_info['population_estimate']
            )
            
            if underserved_score > 30:  # Threshold para área carente
                underserved_areas.append({
                    'region_code': region_code,
                    'name': region_info['name'],
                    'population': region_info['population_estimate'],
                    'penetration': penetration.get('estimated_penetration', 0),
                    'coverage': coverage.get('coverage_level', 'unknown'),
                    'underserved_score': underserved_score,
                    'priority': self._calculate_priority(underserved_score),
                    'recommendations': self._generate_recommendations(
                        region_info,
                        penetration.get('estimated_penetration', 0)
                    )
                })
        
        # Ordenar por score (mais carentes primeiro)
        underserved_areas.sort(key=lambda x: x['underserved_score'], reverse=True)
        
        return underserved_areas
    
    def _calculate_underserved_score(self, penetration, coverage, population):
        """Calcula score de carência (0-100)"""
        # Fatores:
        # - Baixa penetração = mais carente
        # - Baixa cobertura = mais carente
        # - População alta = mais importante
        
        penetration_factor = 100 - penetration  # Inverter: baixo = alto score
        coverage_factor = 100 - coverage
        population_factor = min(100, (population / 200000) * 100)  # Normalizar
        
        # Peso: penetração 40%, cobertura 40%, população 20%
        score = (penetration_factor * 0.4 + coverage_factor * 0.4 + population_factor * 0.2)
        
        return round(score, 2)
    
    def _calculate_priority(self, underserved_score):
        """Calcula prioridade de intervenção"""
        if underserved_score > 70:
            return 'critical'
        elif underserved_score > 50:
            return 'high'
        elif underserved_score > 30:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, region_info, penetration):
        """Gera recomendações específicas para região"""
        recommendations = []
        
        if region_info['type'] == 'insular':
            recommendations.append('Investir em conectividade via satélite')
            recommendations.append('Considerar tecnologias wireless de longo alcance')
        elif region_info['type'] == 'rural':
            recommendations.append('Expandir torres de celular')
            recommendations.append('Implementar incentivos fiscais para operadoras')
        elif region_info['type'] == 'urban':
            recommendations.append('Melhorar qualidade de serviço')
            recommendations.append('Aumentar capacidade de rede')
        
        if penetration < 30:
            recommendations.append('Campanhas de conscientização sobre benefícios de telecomunicações')
            recommendations.append('Programas de subsídio para populações de baixa renda')
        
        return recommendations
    
    # ===== COMPARAÇÃO URBANO-RURAL =====
    
    def compare_urban_rural(self):
        """
        Compara cobertura e penetração entre áreas urbanas e rurais
        
        Returns:
            dict com comparação urbano-rural
        """
        coverage_data = self.generate_coverage_map()
        penetration_data = self.analyze_regional_penetration()
        
        urban_stats = {
            'regions': [],
            'avg_penetration': 0,
            'avg_coverage': 0,
            'total_population': 0
        }
        
        rural_stats = {
            'regions': [],
            'avg_penetration': 0,
            'avg_coverage': 0,
            'total_population': 0
        }
        
        insular_stats = {
            'regions': [],
            'avg_penetration': 0,
            'avg_coverage': 0,
            'total_population': 0
        }
        
        # Agrupar por tipo
        for region_code, region_info in self.REGIONS.items():
            region_type = region_info['type']
            penetration = penetration_data.get(region_code, {}).get('estimated_penetration', 0)
            coverage = coverage_data.get(region_code, {}).get('coverage_percentage', 0)
            population = region_info['population_estimate']
            
            region_data = {
                'name': region_info['name'],
                'penetration': penetration,
                'coverage': coverage,
                'population': population
            }
            
            if region_type == 'urban':
                urban_stats['regions'].append(region_data)
                urban_stats['total_population'] += population
            elif region_type == 'rural':
                rural_stats['regions'].append(region_data)
                rural_stats['total_population'] += population
            elif region_type == 'insular':
                insular_stats['regions'].append(region_data)
                insular_stats['total_population'] += population
        
        # Calcular médias
        for stats in [urban_stats, rural_stats, insular_stats]:
            if stats['regions']:
                stats['avg_penetration'] = round(
                    sum(r['penetration'] for r in stats['regions']) / len(stats['regions']),
                    2
                )
                stats['avg_coverage'] = round(
                    sum(r['coverage'] for r in stats['regions']) / len(stats['regions']),
                    2
                )
        
        # Calcular gap urbano-rural
        penetration_gap = urban_stats['avg_penetration'] - rural_stats['avg_penetration']
        coverage_gap = urban_stats['avg_coverage'] - rural_stats['avg_coverage']
        
        return {
            'urban': urban_stats,
            'rural': rural_stats,
            'insular': insular_stats,
            'digital_divide': {
                'penetration_gap': round(penetration_gap, 2),
                'coverage_gap': round(coverage_gap, 2),
                'severity': 'high' if penetration_gap > 40 else 'medium' if penetration_gap > 20 else 'low'
            }
        }
    
    # ===== INSIGHTS GEOGRÁFICOS =====
    
    def generate_geographic_insights(self):
        """Gera insights automáticos sobre distribuição geográfica"""
        insights = []
        
        # Análise de áreas carentes
        underserved = self.identify_underserved_areas()
        if underserved:
            critical_areas = [a for a in underserved if a['priority'] == 'critical']
            if critical_areas:
                insights.append({
                    'type': 'warning',
                    'category': 'geographic',
                    'title': 'Áreas Críticas Identificadas',
                    'message': f"{len(critical_areas)} região(ões) com cobertura crítica: {', '.join([a['name'] for a in critical_areas[:3]])}",
                    'priority': 'high'
                })
        
        # Análise de divisão digital
        comparison = self.compare_urban_rural()
        digital_divide = comparison['digital_divide']
        if digital_divide['severity'] == 'high':
            insights.append({
                'type': 'warning',
                'category': 'digital_divide',
                'title': 'Divisão Digital Acentuada',
                'message': f"Gap de {digital_divide['penetration_gap']:.1f}% entre áreas urbanas e rurais",
                'priority': 'high'
            })
        
        # Análise de regiões insulares
        if comparison['insular']['avg_penetration'] < 30:
            insights.append({
                'type': 'info',
                'category': 'insular',
                'title': 'Desafio em Regiões Insulares',
                'message': 'Bolama/Bijagós apresenta desafios únicos de conectividade',
                'priority': 'medium'
            })
        
        return insights

