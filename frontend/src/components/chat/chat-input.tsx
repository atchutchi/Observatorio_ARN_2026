import { useState, useRef } from 'react'
import { Send } from 'lucide-react'

type ChatInputProps = {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const ChatInput = ({ onSend, disabled = false, placeholder = 'Escreva a sua pergunta...' }: ChatInputProps) => {
  const [message, setMessage] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    const trimmed = message.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setMessage('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex items-end gap-2 p-4 border-t bg-white">
      <textarea
        ref={inputRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={placeholder}
        rows={1}
        className="flex-1 resize-none input-field text-sm min-h-[40px] max-h-32"
        style={{ height: 'auto', overflowY: message.split('\n').length > 3 ? 'auto' : 'hidden' }}
        aria-label="Mensagem para o assistente"
      />
      <button
        type="button"
        onClick={handleSubmit}
        disabled={disabled || !message.trim()}
        className="btn-primary p-2.5 rounded-xl disabled:opacity-50"
        aria-label="Enviar mensagem"
      >
        <Send className="w-5 h-5" />
      </button>
    </div>
  )
}

export default ChatInput
