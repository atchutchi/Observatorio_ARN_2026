import { Sparkles } from 'lucide-react'

type SuggestedQueriesProps = {
  onSelect: (query: string) => void
}

const SUGGESTIONS = [
  'Qual o total de assinantes móvel no último ano?',
  'Compare receitas de Telecel vs Orange',
  'Qual a quota da Starlink no mercado de internet fixa?',
  'Qual é a taxa de penetração móvel actual?',
  'Analise a evolução do tráfego de dados',
  'Quais indicadores a Starlink reporta?',
]

const SuggestedQueries = ({ onSelect }: SuggestedQueriesProps) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-gray-500">
        <Sparkles className="w-4 h-4" />
        <span className="text-sm font-medium">Sugestões</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onSelect(suggestion)}
            className="text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-xl text-sm text-gray-700 transition-colors border border-gray-100"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}

export default SuggestedQueries
