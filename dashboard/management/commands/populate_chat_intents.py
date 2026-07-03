from django.core.management.base import BaseCommand
from dashboard.models import ChatIntent

class Command(BaseCommand):
    help = 'Popula intenções pré-definidas do chat ARN'

    def handle(self, *args, **options):
        # Intenções pré-definidas
        intents = [
            {
                'nome': 'saudacao',
                'tipo': 'saudacao',
                'palavras_chave': ['ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'hello'],
                'entidades_esperadas': [],
                'template_resposta': 'Olá! Sou o Assistente ARN Analytics. Como posso ajudar com dados de telecomunicações?',
                'query_sql': '',
                'confianca_minima': 0.8
            },
            {
                'nome': 'consulta_assinantes',
                'tipo': 'consulta_assinantes',
                'palavras_chave': ['assinantes', 'clientes', 'utilizadores', 'estações', 'quantos', 'número'],
                'entidades_esperadas': ['operadora', 'periodo', 'ano'],
                'template_resposta': 'Em {ano}, {operadora} tinha {total} assinantes, representando {percentual}% do mercado.',
                'query_sql': 'SELECT operadora, SUM(assinantes_pre_pago + assinantes_pos_pago) as total FROM questionarios_assinantesindicador WHERE ano = %s GROUP BY operadora',
                'confianca_minima': 0.7
            },
            {
                'nome': 'market_share',
                'tipo': 'market_share',
                'palavras_chave': ['quota', 'market share', 'percentagem', 'domínio', 'liderança', 'participação'],
                'entidades_esperadas': ['operadora', 'ano'],
                'template_resposta': 'A {operadora} detém {percentual}% do mercado em {ano}.',
                'query_sql': 'SELECT operadora, COUNT(*) as total FROM estacoes_moveis GROUP BY operadora',
                'confianca_minima': 0.7
            },
            {
                'nome': 'analise_trafego',
                'tipo': 'analise_trafego',
                'palavras_chave': ['tráfego', 'trafego', 'chamadas', 'minutos', 'voz', 'volume', 'on-net', 'off-net'],
                'entidades_esperadas': ['operadora', 'tipo_trafego', 'ano'],
                'template_resposta': 'O tráfego {tipo} da {operadora} foi de {volume} minutos em {ano}.',
                'query_sql': 'SELECT tipo, SUM(minutos) FROM trafego_voz WHERE operadora = %s GROUP BY tipo',
                'confianca_minima': 0.7
            },
            {
                'nome': 'receitas',
                'tipo': 'receitas',
                'palavras_chave': ['receitas', 'faturamento', 'volume de negócios', 'FCFA', 'lucro', 'rendimento'],
                'entidades_esperadas': ['operadora', 'ano'],
                'template_resposta': 'A receita da {operadora} foi de {valor} milhões FCFA em {ano}.',
                'query_sql': 'SELECT SUM(receita_total) FROM receitas WHERE operadora = %s AND ano = %s',
                'confianca_minima': 0.7
            },
            {
                'nome': 'comparacao_operadores',
                'tipo': 'comparacao_operadores',
                'palavras_chave': ['comparar', 'versus', 'vs', 'diferença', 'melhor', 'maior', 'contra'],
                'entidades_esperadas': ['operadora1', 'operadora2', 'metrica'],
                'template_resposta': 'Comparando {operadora1} e {operadora2}: {analise_comparativa}',
                'query_sql': 'SELECT operadora, metrica FROM dados WHERE operadora IN (%s, %s)',
                'confianca_minima': 0.7
            },
            {
                'nome': 'tendencias',
                'tipo': 'tendencias',
                'palavras_chave': ['tendência', 'evolução', 'crescimento', 'queda', 'variação', 'histórico'],
                'entidades_esperadas': ['indicador', 'periodo'],
                'template_resposta': 'O {indicador} apresentou {tipo_variacao} de {percentual}% no período analisado.',
                'query_sql': 'SELECT periodo, valor FROM indicadores WHERE nome = %s ORDER BY periodo',
                'confianca_minima': 0.6
            },
            {
                'nome': 'investimentos',
                'tipo': 'investimentos',
                'palavras_chave': ['investimento', 'CAPEX', 'infraestrutura', 'gastos', 'aplicação'],
                'entidades_esperadas': ['operadora', 'tipo_investimento', 'ano'],
                'template_resposta': 'Os investimentos em {tipo} totalizaram {valor} FCFA em {ano}.',
                'query_sql': 'SELECT tipo, SUM(valor) FROM investimentos WHERE operadora = %s GROUP BY tipo',
                'confianca_minima': 0.7
            },
            {
                'nome': 'banda_larga',
                'tipo': 'banda_larga',
                'palavras_chave': ['internet', 'dados', '3G', '4G', '5G', 'banda larga', 'download', 'upload'],
                'entidades_esperadas': ['tecnologia', 'operadora', 'ano'],
                'template_resposta': 'A tecnologia {tecnologia} tem {assinantes} utilizadores em {ano}.',
                'query_sql': 'SELECT tecnologia, COUNT(*) FROM banda_larga WHERE operadora = %s GROUP BY tecnologia',
                'confianca_minima': 0.7
            },
            {
                'nome': 'emprego',
                'tipo': 'emprego',
                'palavras_chave': ['emprego', 'funcionários', 'trabalhadores', 'pessoal', 'RH', 'empregos'],
                'entidades_esperadas': ['operadora', 'tipo_emprego'],
                'template_resposta': 'A {operadora} emprega {total} pessoas, sendo {diretos} diretos e {indiretos} indiretos.',
                'query_sql': 'SELECT tipo, COUNT(*) FROM empregos WHERE operadora = %s GROUP BY tipo',
                'confianca_minima': 0.7
            },
            {
                'nome': 'despedida',
                'tipo': 'despedida',
                'palavras_chave': ['tchau', 'adeus', 'até logo', 'obrigado', 'valeu', 'bye'],
                'entidades_esperadas': [],
                'template_resposta': 'Obrigado por usar o Assistente ARN! Foi um prazer ajudar com os dados de telecomunicações. Até breve!',
                'query_sql': '',
                'confianca_minima': 0.8
            },
            {
                'nome': 'nao_entendido',
                'tipo': 'nao_entendido',
                'palavras_chave': [],
                'entidades_esperadas': [],
                'template_resposta': 'Desculpe, não entendi sua pergunta. Posso ajudar com dados sobre assinantes, receitas, tráfego ou market share. Tente reformular sua pergunta.',
                'query_sql': '',
                'confianca_minima': 0.0
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for intent_data in intents:
            intent, created = ChatIntent.objects.update_or_create(
                nome=intent_data['nome'],
                defaults=intent_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Intenção criada: {intent.nome}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Intenção atualizada: {intent.nome}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Concluído! {created_count} intenções criadas, {updated_count} atualizadas.'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🤖 Assistente ARN Analytics configurado e pronto para uso!'
            )
        )
