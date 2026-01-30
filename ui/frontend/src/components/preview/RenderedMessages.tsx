import { cn } from '../../lib/utils'

interface RenderedMessagesProps {
  messages: { role: string; content: string }[]
}

export function RenderedMessages({ messages }: RenderedMessagesProps) {
  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Click "Render" to preview the prompt
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className="rounded border border-border">
            <div
              className={cn(
                'px-3 py-1.5 text-xs font-medium',
                msg.role === 'system' && 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300',
                msg.role === 'user' && 'bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300',
                msg.role === 'assistant' && 'bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300'
              )}
            >
              {msg.role}
            </div>
            <div className="whitespace-pre-wrap p-3 font-mono text-xs leading-relaxed">
              {msg.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
