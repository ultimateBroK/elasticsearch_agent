import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Message } from "@/store/chatStore"
import { ChartRenderer } from "@/components/charts/ChartRenderer"
import { IntelligenceInsights } from "@/components/IntelligenceInsights"

interface ChatMessageProps {
  message: Message
  onRetry?: () => void
  onSuggestionClick?: (suggestion: string) => void
  onFeedback?: (feedback: { satisfaction: number; chart_rating: number }) => void
}

export function ChatMessage({ message, onRetry, onSuggestionClick, onFeedback }: ChatMessageProps) {
  const isUser = message.sender === 'user'
  const isError = message.error
  
  return (
    <div className={cn(
      "flex w-full mb-4",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "max-w-[80%] md:max-w-[60%]",
        isUser ? "ml-auto" : "mr-auto"
      )}>
        <Card className={cn(
          "transition-colors",
          isUser 
            ? "bg-primary text-primary-foreground ml-auto" 
            : isError
            ? "bg-red-50 border-red-200"
            : "bg-muted"
        )}>
          <CardContent className="p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="text-xs font-medium opacity-70">
                {isUser ? "You" : "Agent"}
              </div>
              {message.intent && !isUser && (
                <Badge variant="outline" className="text-xs">
                  {message.intent}
                </Badge>
              )}
              {isError && (
                <Badge variant="destructive" className="text-xs">
                  Error
                </Badge>
              )}
            </div>
            
            <div className={cn(
              "text-sm",
              isError && !isUser && "text-red-700"
            )}>
              {message.content}
            </div>
            
            {/* Retry button for retryable errors */}
            {isError && message.retryable && onRetry && (
              <div className="mt-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onRetry}
                  className="text-xs"
                >
                  Retry
                </Button>
              </div>
            )}
            
            {/* Chart Visualization */}
            {message.chartConfig && message.data && !isError && (
              <ChartRenderer 
                chartConfig={message.chartConfig} 
                data={message.data} 
              />
            )}
            
            {/* Intelligence Insights */}
            {!isUser && !isError && (message.queryInsight || message.personalizedSuggestions || message.intelligenceMetrics) && (
              <IntelligenceInsights
                queryInsight={message.queryInsight}
                personalizedSuggestions={message.personalizedSuggestions}
                intelligenceMetrics={message.intelligenceMetrics}
                onSuggestionClick={onSuggestionClick}
                onFeedback={onFeedback}
              />
            )}
            
            <div className={cn(
              "text-xs mt-2 opacity-60",
              isUser ? "text-right" : "text-left"
            )}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 