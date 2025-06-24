import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Send, Loader2 } from "lucide-react"

interface MessageInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
  placeholder?: string
}

export function MessageInput({ 
  onSendMessage, 
  isLoading, 
  placeholder = "Type your message..." 
}: MessageInputProps) {
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Clear previous errors
    setError("")
    
    // Validation
    if (!message.trim()) {
      setError("Message cannot be empty")
      return
    }
    
    if (message.length > 1000) {
      setError("Message too long (max 1000 characters)")
      return
    }
    
    if (!isLoading) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setMessage(value)
    
    // Clear error when user starts typing
    if (error) {
      setError("")
    }
    
    // Show character count warning
    if (value.length > 900) {
      setError(`${1000 - value.length} characters remaining`)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <Card className="border-t">
      <CardContent className="p-4">
        {error && (
          <div className={`text-xs mb-2 ${
            error.includes('remaining') ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={message}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={isLoading}
            className={`flex-1 ${error && !error.includes('remaining') ? 'border-red-300' : ''}`}
            maxLength={1000}
          />
          
          <Button 
            type="submit" 
            disabled={!message.trim() || isLoading || message.length > 1000}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
        
        <div className="text-xs text-muted-foreground mt-1 text-right">
          {message.length}/1000
        </div>
      </CardContent>
    </Card>
  )
} 