"""
Serviço de Análise de Competitividade de Preços - ARN
Comparação de tarifários entre operadoras
"""
from decimal import Decimal
from django.db.models import Avg, Min, Max, Count

from questionarios.models import (
    TarifarioVozOrangeIndicador,
    TarifarioVozMTNIndicador,
    TarifarioVozTelecelIndicador
)


class PriceAnalysisService:
    """
    Análise de competitividade de preços entre operadoras
    Comparação de tarifários e identificação de melhores ofertas
    """
    
    def __init__(self, year=None):
        from django.utils import timezone
        self.year = year or timezone.now().year
    
    # ===== COMPARAÇÃO DE PREÇOS ENTRE OPERADORAS =====
    
    def compare_operator_prices(self):
        """
        Compara preços entre todas as operadoras
        
        Returns:
            dict com comparação detalhada de preços
        """
        comparison = {
            'internet_movel': self._compare_internet_prices(),
            'chamadas_on_net': self._compare_onnet_prices(),
            'chamadas_off_net': self._compare_offnet_prices(),
            'chamadas_internacionais': self._compare_international_prices(),
            'pacotes_dados': self._compare_data_packages()
        }
        
        return comparison
    
    def _compare_internet_prices(self):
        """Compara preços de internet móvel"""
        prices = {}
        
        # Orange
        try:
            orange_data = TarifarioVozOrangeIndicador.objects.filter(
                ano=self.year
            ).first()
            
            if orange_data:
                # Pegar preços de internet USB pré-pago
                prices['ORANGE'] = {
                    'usb_1gb': float(orange_data.internet_usb_prepago_1gb or 0),
                    'usb_3gb': float(orange_data.internet_usb_prepago_3gb or 0),
                    'usb_5gb': float(orange_data.internet_usb_prepago_5gb or 0),
                    'usb_10gb': float(orange_data.internet_usb_prepago_10gb or 0)
                }
        except Exception as e:
            prices['ORANGE'] = {'error': str(e)}
        
        # MTN (se disponível)
        try:
            mtn_data = TarifarioVozMTNIndicador.objects.filter(
                ano=self.year
            ).first()
            
            if mtn_data:
                prices['MTN'] = {
                    'pacote_diario': float(mtn_data.pacote_diario_preco or 0),
                    'pacote_semanal': float(mtn_data.pacote_semanal_preco or 0),
                    'pacote_mensal': float(mtn_data.pacote_mensal_preco or 0)
                }
        except Exception as e:
            prices['MTN'] = {'error': str(e)}
        
        # Telecel
        try:
            telecel_data = TarifarioVozTelecelIndicador.objects.filter(
                ano=self.year
            ).first()
            
            if telecel_data:
                prices['TELECEL'] = {
                    # Adicionar campos de preços quando disponíveis
                    'available': True
                }
        except Exception as e:
            prices['TELECEL'] = {'error': str(e)}
        
        return prices
    
    def _compare_onnet_prices(self):
        """Compara preços de chamadas on-net"""
        prices = {}
        
        # Orange
        try:
            orange_data = TarifarioVozOrangeIndicador.objects.filter(ano=self.year).first()
            if orange_data:
                prices['ORANGE'] = {
                    'on_net_prepago': float(orange_data.chamada_on_net_prepago or 0),
                    'on_net_pospago': float(orange_data.chamada_on_net_pospago or 0)
                }
        except:
            prices['ORANGE'] = {}
        
        # MTN
        try:
            mtn_data = TarifarioVozMTNIndicador.objects.filter(ano=self.year).first()
            if mtn_data:
                prices['MTN'] = {
                    'on_net': float(mtn_data.chamada_on_net or 0)
                }
        except:
            prices['MTN'] = {}
        
        # Telecel
        try:
            telecel_data = TarifarioVozTelecelIndicador.objects.filter(ano=self.year).first()
            if telecel_data:
                prices['TELECEL'] = {
                    'on_net': float(telecel_data.chamada_on_net or 0)
                }
        except:
            prices['TELECEL'] = {}
        
        return prices
    
    def _compare_offnet_prices(self):
        """Compara preços de chamadas off-net"""
        prices = {}
        
        # Orange
        try:
            orange_data = TarifarioVozOrangeIndicador.objects.filter(ano=self.year).first()
            if orange_data:
                prices['ORANGE'] = {
                    'off_net_prepago': float(orange_data.chamada_off_net_prepago or 0),
                    'off_net_pospago': float(orange_data.chamada_off_net_pospago or 0)
                }
        except:
            prices['ORANGE'] = {}
        
        # MTN
        try:
            mtn_data = TarifarioVozMTNIndicador.objects.filter(ano=self.year).first()
            if mtn_data:
                prices['MTN'] = {
                    'off_net': float(mtn_data.chamada_off_net or 0)
                }
        except:
            prices['MTN'] = {}
        
        # Telecel
        try:
            telecel_data = TarifarioVozTelecelIndicador.objects.filter(ano=self.year).first()
            if telecel_data:
                prices['TELECEL'] = {
                    'off_net': float(telecel_data.chamada_off_net or 0)
                }
        except:
            prices['TELECEL'] = {}
        
        return prices
    
    def _compare_international_prices(self):
        """Compara preços de chamadas internacionais"""
        prices = {}
        
        # Orange - tarifas por zona
        try:
            orange_data = TarifarioVozOrangeIndicador.objects.filter(ano=self.year).first()
            if orange_data:
                prices['ORANGE'] = {
                    'zona_1': float(orange_data.internacional_zona_1 or 0),
                    'zona_2': float(orange_data.internacional_zona_2 or 0),
                    'zona_3': float(orange_data.internacional_zona_3 or 0)
                }
        except:
            prices['ORANGE'] = {}
        
        return prices
    
    def _compare_data_packages(self):
        """Compara pacotes de dados"""
        packages = {}
        
        # Orange
        try:
            orange_data = TarifarioVozOrangeIndicador.objects.filter(ano=self.year).first()
            if orange_data:
                packages['ORANGE'] = [
                    {'size': '1GB', 'price': float(orange_data.internet_usb_prepago_1gb or 0)},
                    {'size': '3GB', 'price': float(orange_data.internet_usb_prepago_3gb or 0)},
                    {'size': '5GB', 'price': float(orange_data.internet_usb_prepago_5gb or 0)},
                    {'size': '10GB', 'price': float(orange_data.internet_usb_prepago_10gb or 0)}
                ]
        except:
            packages['ORANGE'] = []
        
        # MTN
        try:
            mtn_data = TarifarioVozMTNIndicador.objects.filter(ano=self.year).first()
            if mtn_data:
                packages['MTN'] = [
                    {'period': 'Diário', 'price': float(mtn_data.pacote_diario_preco or 0)},
                    {'period': 'Semanal', 'price': float(mtn_data.pacote_semanal_preco or 0)},
                    {'period': 'Mensal', 'price': float(mtn_data.pacote_mensal_preco or 0)}
                ]
        except:
            packages['MTN'] = []
        
        return packages
    
    # ===== IDENTIFICAÇÃO DE MELHORES OFERTAS =====
    
    def identify_best_deals(self):
        """
        Identifica as melhores ofertas para consumidores
        
        Returns:
            dict com melhores ofertas por categoria
        """
        price_comparison = self.compare_operator_prices()
        best_deals = {}
        
        # Melhor preço para internet móvel
        internet_prices = price_comparison.get('internet_movel', {})
        if internet_prices:
            best_deals['internet'] = self._find_best_internet_deal(internet_prices)
        
        # Melhor preço para chamadas on-net
        onnet_prices = price_comparison.get('chamadas_on_net', {})
        if onnet_prices:
            best_deals['on_net'] = self._find_cheapest_onnet(onnet_prices)
        
        # Melhor preço para chamadas off-net
        offnet_prices = price_comparison.get('chamadas_off_net', {})
        if offnet_prices:
            best_deals['off_net'] = self._find_cheapest_offnet(offnet_prices)
        
        return best_deals
    
    def _find_best_internet_deal(self, internet_prices):
        """Encontra melhor oferta de internet"""
        best_deal = None
        best_price_per_gb = float('inf')
        
        for operator, prices in internet_prices.items():
            if isinstance(prices, dict) and 'error' not in prices:
                # Para Orange, calcular preço por GB
                if 'usb_1gb' in prices and prices['usb_1gb'] > 0:
                    price_per_gb = prices['usb_1gb']
                    if price_per_gb < best_price_per_gb:
                        best_price_per_gb = price_per_gb
                        best_deal = {
                            'operator': operator,
                            'package': '1GB',
                            'price': price_per_gb,
                            'price_per_gb': price_per_gb
                        }
        
        return best_deal
    
    def _find_cheapest_onnet(self, onnet_prices):
        """Encontra operadora mais barata para on-net"""
        cheapest = None
        lowest_price = float('inf')
        
        for operator, prices in onnet_prices.items():
            if isinstance(prices, dict):
                # Pegar o preço mais baixo (prepago ou pospago)
                price = min([p for p in prices.values() if p > 0], default=float('inf'))
                if price < lowest_price:
                    lowest_price = price
                    cheapest = {
                        'operator': operator,
                        'price_per_minute': price
                    }
        
        return cheapest
    
    def _find_cheapest_offnet(self, offnet_prices):
        """Encontra operadora mais barata para off-net"""
        cheapest = None
        lowest_price = float('inf')
        
        for operator, prices in offnet_prices.items():
            if isinstance(prices, dict):
                price = min([p for p in prices.values() if p > 0], default=float('inf'))
                if price < lowest_price:
                    lowest_price = price
                    cheapest = {
                        'operator': operator,
                        'price_per_minute': price
                    }
        
        return cheapest
    
    # ===== ÍNDICE DE PREÇOS DO MERCADO =====
    
    def calculate_price_index(self):
        """
        Calcula índice de preços do mercado
        Baseado em cesta básica de serviços de telecomunicações
        
        Returns:
            dict com índice de preços
        """
        price_comparison = self.compare_operator_prices()
        
        # Definir cesta básica (pesos)
        basket = {
            'chamadas_on_net': 0.3,  # 30% do peso
            'chamadas_off_net': 0.3,  # 30% do peso
            'internet_1gb': 0.4  # 40% do peso
        }
        
        # Calcular preço médio de mercado para cada serviço
        avg_prices = {}
        
        # Chamadas on-net
        onnet_prices = [
            p for operator, prices in price_comparison.get('chamadas_on_net', {}).items()
            for p in prices.values() if isinstance(p, (int, float)) and p > 0
        ]
        avg_prices['on_net'] = sum(onnet_prices) / len(onnet_prices) if onnet_prices else 0
        
        # Chamadas off-net
        offnet_prices = [
            p for operator, prices in price_comparison.get('chamadas_off_net', {}).items()
            for p in prices.values() if isinstance(p, (int, float)) and p > 0
        ]
        avg_prices['off_net'] = sum(offnet_prices) / len(offnet_prices) if offnet_prices else 0
        
        # Internet 1GB
        internet_prices = []
        for operator, prices in price_comparison.get('internet_movel', {}).items():
            if isinstance(prices, dict) and 'usb_1gb' in prices and prices['usb_1gb'] > 0:
                internet_prices.append(prices['usb_1gb'])
        avg_prices['internet'] = sum(internet_prices) / len(internet_prices) if internet_prices else 0
        
        # Calcular índice ponderado (base 100)
        index_value = (
            avg_prices['on_net'] * basket['chamadas_on_net'] +
            avg_prices['off_net'] * basket['chamadas_off_net'] +
            avg_prices['internet'] * basket['internet_1gb']
        )
        
        return {
            'index_value': round(index_value, 2),
            'base_year': self.year,
            'components': {
                'on_net_avg': round(avg_prices['on_net'], 2),
                'off_net_avg': round(avg_prices['off_net'], 2),
                'internet_1gb_avg': round(avg_prices['internet'], 2)
            },
            'basket_weights': basket
        }
    
    # ===== EVOLUÇÃO HISTÓRICA DE PREÇOS =====
    
    def analyze_price_evolution(self, years_back=3):
        """
        Analisa evolução de preços ao longo do tempo
        
        Args:
            years_back: Número de anos para analisar
        
        Returns:
            dict com evolução histórica
        """
        evolution = []
        current_year = self.year
        
        for year in range(current_year - years_back, current_year + 1):
            # Criar instância temporária para o ano
            temp_service = PriceAnalysisService(year=year)
            index = temp_service.calculate_price_index()
            
            evolution.append({
                'year': year,
                'index': index['index_value'],
                'components': index['components']
            })
        
        # Calcular tendência
        if len(evolution) >= 2:
            first_index = evolution[0]['index']
            last_index = evolution[-1]['index']
            change_percentage = ((last_index - first_index) / first_index * 100) if first_index > 0 else 0
            trend = 'increasing' if change_percentage > 5 else 'decreasing' if change_percentage < -5 else 'stable'
        else:
            change_percentage = 0
            trend = 'unknown'
        
        return {
            'evolution': evolution,
            'overall_change_percentage': round(change_percentage, 2),
            'trend': trend,
            'years_analyzed': len(evolution)
        }
    
    # ===== INSIGHTS DE PREÇOS =====
    
    def generate_price_insights(self):
        """Gera insights automáticos sobre preços"""
        insights = []
        
        # Melhores ofertas
        best_deals = self.identify_best_deals()
        if best_deals.get('internet'):
            deal = best_deals['internet']
            insights.append({
                'type': 'info',
                'category': 'pricing',
                'title': 'Melhor Oferta de Internet',
                'message': f"{deal['operator']} oferece {deal['package']} por {deal['price']:.0f} FCFA",
                'priority': 'medium'
            })
        
        # Evolução de preços
        try:
            evolution = self.analyze_price_evolution(years_back=2)
            if evolution['trend'] == 'decreasing':
                insights.append({
                    'type': 'positive',
                    'category': 'pricing',
                    'title': 'Preços em Queda',
                    'message': f"Preços caíram {abs(evolution['overall_change_percentage']):.1f}% nos últimos 2 anos",
                    'priority': 'medium'
                })
            elif evolution['trend'] == 'increasing':
                insights.append({
                    'type': 'warning',
                    'category': 'pricing',
                    'title': 'Preços em Alta',
                    'message': f"Preços subiram {evolution['overall_change_percentage']:.1f}% nos últimos 2 anos",
                    'priority': 'high'
                })
        except:
            pass
        
        return insights
    
    # ===== COMPARADOR PÚBLICO =====
    
    def get_public_price_comparison(self):
        """
        Retorna comparação de preços em formato amigável para público
        
        Returns:
            dict formatado para exibição pública
        """
        comparison = self.compare_operator_prices()
        best_deals = self.identify_best_deals()
        
        return {
            'last_updated': self.year,
            'disclaimer': 'Preços sujeitos a alteração. Consulte a operadora para valores atualizados.',
            'comparison': comparison,
            'recommendations': best_deals,
            'price_index': self.calculate_price_index()
        }

