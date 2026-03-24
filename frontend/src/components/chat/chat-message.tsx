import { Bot, User } from 'lucide-react'
import { cn } from '@/lib/utils'

type ChatMessageProps = {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

const ChatMessage = ({ role, content, timestamp }: ChatMessageProps) => {
  const isUser = role === 'user'

  return (
    <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div className={cn(
        'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
        isUser ? 'bg-arn-primary' : 'bg-gradient-to-br from-blue-500 to-purple-600',
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      <div className={cn(
        'max-w-[75%] rounded-2xl px-4 py-3',
        isUser
          ? 'bg-arn-primary text-white rounded-tr-sm'
          : 'bg-gray-100 text-gray-900 rounded-tl-sm',
      )}>
        <div className="text-sm whitespace-pre-wrap leading-relaxed">{content}</div>
        {timestamp && (
          <p className={cn(
            'text-xs mt-1',
            isUser ? 'text-white/60' : 'text-gray-400',
          )}>
            {new Date(timestamp).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
