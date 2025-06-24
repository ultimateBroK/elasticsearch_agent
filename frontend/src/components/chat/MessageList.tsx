import { useEffect, useRef } from "react"
import { ChatMessage } from "./ChatMessage"
import { Message } from "@/store/chatStore"
import { ScrollArea } from "@/components/ui/scroll-area"

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  onRetryMessage?: (messageId: string) => void
}

export function MessageList({ messages, isLoading, onRetryMessage }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <ScrollArea className="flex-1 p-4">
      <div className="space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground py-12">
            <div className="text-lg mb-2">👋 Welcome to Elasticsearch Agent!</div>
            <div className="text-sm">
              Ask me anything about your data and I'll help you visualize it.
            </div>
            <div className="text-xs mt-2 opacity-60">
              Try: "Show me the latest data" or "Create a chart of sales"
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage 
              key={message.id} 
              message={message} 
              onRetry={onRetryMessage ? () => onRetryMessage(message.id) : undefined}
            />
          ))
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] md:max-w-[60%]">
              <div className="bg-muted rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                  </div>
                  <span className="text-sm text-muted-foreground">Agent is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
} 