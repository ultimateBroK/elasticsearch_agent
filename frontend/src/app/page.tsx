import { ChatInterface } from "@/components/chat/ChatInterface"
import { ErrorBoundary } from "@/components/ErrorBoundary"

export default function Home() {
  return (
    <main className="container mx-auto p-4 h-screen">
      <ErrorBoundary>
        <ChatInterface />
      </ErrorBoundary>
    </main>
  )
}
