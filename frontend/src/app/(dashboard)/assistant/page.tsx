'use client'

import { useState, useRef, useEffect } from 'react'
import { Bot, Loader2 } from 'lucide-react'
import ChatMessage from '@/components/chat/chat-message'
import ChatInput from '@/components/chat/chat-input'
import SuggestedQueries from '@/components/chat/suggested-queries'
import api from '@/lib/api'

type Message = {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

const AssistantPage = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [isThinking, setIsThinking] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages, isThinking])

  const handleSend = async (message: string) => {
    const tempId = Date.now()
    const userMsg: Message = {
      id: tempId,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsThinking(true)

    try {
      const payload: Record<string, string | number | null> = { message }
      if (sessionId) payload.session_id = sessionId

      const res = await api.post('/assistant/query/', payload)

      setSessionId(res.data.session_id)
      const assistantMsg: Message = {
        id: res.data.message.id,
        role: 'assistant',
        content: res.data.message.content,
        created_at: res.data.message.created_at,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch {
      const errorMsg: Message = {
        id: tempId + 1,
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar a sua pergunta. Tente novamente.',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsThinking(false)
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setSessionId(null)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex items-center justify-between px-6 py-4 border-b">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Assistente IA</h2>
            <p className="text-xs text-gray-500">Observatório Telecom GB — Powered by Gemini</p>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={handleNewChat}
            className="btn-secondary text-xs"
          >
            Nova conversa
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full space-y-8">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mx-auto mb-4">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Assistente do Observatório</h3>
              <p className="text-sm text-gray-500 mt-2 max-w-md">
                Faça perguntas sobre o mercado de telecomunicações da Guiné-Bissau.
                Posso analisar dados de assinantes, receitas, tráfego e mais.
              </p>
            </div>
            <SuggestedQueries onSelect={handleSend} />
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                role={msg.role}
                content={msg.content}
                timestamp={msg.created_at}
              />
            ))}
            {isThinking && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex items-center gap-2 text-gray-500 text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    A pensar...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <ChatInput onSend={handleSend} disabled={isThinking} />
    </div>
  )
}

export default AssistantPage
