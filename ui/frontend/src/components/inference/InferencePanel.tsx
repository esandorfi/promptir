import { useState } from 'react'
import { Play, Copy, Check } from 'lucide-react'
import { Button, Select, Input } from '../ui'
import { useModels, useInference } from '../../hooks/useInference'
import { useWorkbenchStore } from '../../stores/workbench'
import { formatCost, formatLatency, formatTokens, cn } from '../../lib/utils'
import type { InferenceResponse } from '../../types'

interface InferencePanelProps {
  messages: { role: string; content: string }[]
}

export function InferencePanel({ messages }: InferencePanelProps) {
  const { data: models } = useModels()
  const inference = useInference()

  const model = useWorkbenchStore((s) => s.inferenceModel)
  const setModel = useWorkbenchStore((s) => s.setInferenceModel)
  const temperature = useWorkbenchStore((s) => s.inferenceTemp)
  const setTemperature = useWorkbenchStore((s) => s.setInferenceTemp)
  const maxTokens = useWorkbenchStore((s) => s.inferenceMaxTokens)
  const setMaxTokens = useWorkbenchStore((s) => s.setInferenceMaxTokens)

  const [response, setResponse] = useState<InferenceResponse | null>(null)
  const [copied, setCopied] = useState(false)

  const handleRun = () => {
    if (messages.length === 0) return

    inference.mutate(
      {
        messages,
        model,
        temperature,
        max_tokens: maxTokens,
      },
      {
        onSuccess: (data) => {
          setResponse(data)
        },
      }
    )
  }

  const handleCopy = () => {
    if (response) {
      navigator.clipboard.writeText(response.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Controls */}
      <div className="flex items-center gap-3 border-b border-border p-3">
        <Select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="w-48"
        >
          {(models || []).map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </Select>

        <div className="flex items-center gap-1.5">
          <label className="text-xs text-muted-foreground">Temp:</label>
          <Input
            type="number"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            min={0}
            max={2}
            step={0.1}
            className="w-16 text-xs"
          />
        </div>

        <div className="flex items-center gap-1.5">
          <label className="text-xs text-muted-foreground">Max:</label>
          <Input
            type="number"
            value={maxTokens}
            onChange={(e) => setMaxTokens(parseInt(e.target.value))}
            min={1}
            max={4096}
            step={256}
            className="w-20 text-xs"
          />
        </div>

        <div className="flex-1" />

        <Button
          onClick={handleRun}
          disabled={messages.length === 0 || inference.isPending}
        >
          <Play className="mr-1.5 h-3.5 w-3.5" />
          {inference.isPending ? 'Running...' : 'Run'}
        </Button>
      </div>

      {/* Response */}
      <div className="flex-1 overflow-y-auto p-4">
        {inference.error && (
          <div className="rounded border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
            {inference.error.message}
          </div>
        )}

        {response && (
          <div className="space-y-3">
            {/* Stats bar */}
            <div className="flex items-center gap-4 rounded bg-muted/50 px-3 py-2 text-xs">
              <span>
                <span className="text-muted-foreground">Model:</span>{' '}
                <span className="font-medium">{response.model}</span>
              </span>
              <span>
                <span className="text-muted-foreground">Latency:</span>{' '}
                <span className="font-medium">{formatLatency(response.latency_ms)}</span>
              </span>
              <span>
                <span className="text-muted-foreground">In:</span>{' '}
                <span className="font-medium">{formatTokens(response.input_tokens)}</span>
              </span>
              <span>
                <span className="text-muted-foreground">Out:</span>{' '}
                <span className="font-medium">{formatTokens(response.output_tokens)}</span>
              </span>
              <span>
                <span className="text-muted-foreground">Cost:</span>{' '}
                <span className="font-medium">{formatCost(response.cost_estimate)}</span>
              </span>

              <div className="flex-1" />

              <Button variant="ghost" size="sm" onClick={handleCopy}>
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-green-500" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
              </Button>
            </div>

            {/* Response content */}
            <div className="rounded border border-border">
              <div className="bg-purple-50 px-3 py-1.5 text-xs font-medium text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                assistant
              </div>
              <div className="whitespace-pre-wrap p-3 font-mono text-xs leading-relaxed">
                {response.content}
              </div>
            </div>
          </div>
        )}

        {!response && !inference.error && messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            Render the prompt first, then run inference
          </div>
        )}

        {!response && !inference.error && messages.length > 0 && (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            Click "Run" to send the prompt to the LLM
          </div>
        )}
      </div>
    </div>
  )
}
