import { useState, useCallback, useEffect } from 'react'
import { ChevronUp, ChevronDown, Play, Save } from 'lucide-react'
import { Button, Input, Textarea, Select } from '../ui'
import { RenderedMessages } from './RenderedMessages'
import { InferencePanel } from '../inference/InferencePanel'
import { useRender } from '../../hooks/usePrompts'
import { useWorkbenchStore } from '../../stores/workbench'
import { cn, formatTokens } from '../../lib/utils'
import type { PromptDetail, RenderResponse } from '../../types'

interface PreviewPanelProps {
  prompt: PromptDetail | undefined
}

export function PreviewPanel({ prompt }: PreviewPanelProps) {
  const previewExpanded = useWorkbenchStore((s) => s.previewExpanded)
  const setPreviewExpanded = useWorkbenchStore((s) => s.setPreviewExpanded)
  const testVars = useWorkbenchStore((s) => s.testVars)
  const setTestVars = useWorkbenchStore((s) => s.setTestVars)
  const testBlocks = useWorkbenchStore((s) => s.testBlocks)
  const setTestBlocks = useWorkbenchStore((s) => s.setTestBlocks)

  const [rendered, setRendered] = useState<RenderResponse | null>(null)
  const [activeTab, setActiveTab] = useState<'inputs' | 'rendered' | 'inference'>('inputs')

  const render = useRender()

  // Initialize test inputs when prompt changes
  useEffect(() => {
    if (prompt) {
      const vars: Record<string, string> = {}
      for (const v of prompt.variables) {
        vars[v] = testVars[v] || ''
      }
      setTestVars(vars)

      const blocks: Record<string, string> = {}
      for (const b of Object.keys(prompt.blocks)) {
        blocks[b] = testBlocks[b] || prompt.blocks[b].default
      }
      setTestBlocks(blocks)
    }
  }, [prompt?.id, prompt?.version])

  const handleRender = useCallback(() => {
    if (!prompt) return

    render.mutate(
      {
        prompt_id: prompt.id,
        version: prompt.version,
        vars: testVars,
        blocks: testBlocks,
      },
      {
        onSuccess: (data) => {
          setRendered(data)
          setActiveTab('rendered')
        },
      }
    )
  }, [prompt, testVars, testBlocks, render])

  if (!prompt) {
    return null
  }

  return (
    <div
      className={cn(
        'flex flex-col border-t border-border bg-background transition-all',
        previewExpanded ? 'h-[45%]' : 'h-10'
      )}
    >
      {/* Header */}
      <button
        onClick={() => setPreviewExpanded(!previewExpanded)}
        className="flex h-10 items-center justify-between border-b border-border px-4 hover:bg-muted/50"
      >
        <span className="text-sm font-medium">Preview & Test</span>
        <div className="flex items-center gap-2">
          {rendered && (
            <span className="text-xs text-muted-foreground">
              ~{formatTokens(rendered.token_estimate)} tokens
            </span>
          )}
          {previewExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronUp className="h-4 w-4" />
          )}
        </div>
      </button>

      {previewExpanded && (
        <div className="flex flex-1 overflow-hidden">
          {/* Tabs */}
          <div className="flex w-24 flex-col border-r border-border bg-muted/30">
            {(['inputs', 'rendered', 'inference'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  'px-3 py-2 text-left text-xs font-medium capitalize',
                  activeTab === tab
                    ? 'bg-background text-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {tab}
              </button>
            ))}

            <div className="flex-1" />

            <div className="border-t border-border p-2">
              <Button
                size="sm"
                className="w-full"
                onClick={handleRender}
                disabled={render.isPending}
              >
                <Play className="mr-1 h-3 w-3" />
                {render.isPending ? '...' : 'Render'}
              </Button>
            </div>
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'inputs' && (
              <TestInputs
                variables={prompt.variables}
                blocks={prompt.blocks}
                testVars={testVars}
                setTestVars={setTestVars}
                testBlocks={testBlocks}
                setTestBlocks={setTestBlocks}
              />
            )}
            {activeTab === 'rendered' && (
              <RenderedMessages messages={rendered?.messages || []} />
            )}
            {activeTab === 'inference' && (
              <InferencePanel messages={rendered?.messages || []} />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

interface TestInputsProps {
  variables: string[]
  blocks: Record<string, { optional: boolean; default: string }>
  testVars: Record<string, string>
  setTestVars: (vars: Record<string, string>) => void
  testBlocks: Record<string, string>
  setTestBlocks: (blocks: Record<string, string>) => void
}

function TestInputs({
  variables,
  blocks,
  testVars,
  setTestVars,
  testBlocks,
  setTestBlocks,
}: TestInputsProps) {
  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="grid gap-4 md:grid-cols-2">
        {/* Variables */}
        <div>
          <h4 className="mb-2 text-xs font-medium text-muted-foreground">
            Variables (required)
          </h4>
          <div className="space-y-2">
            {variables.map((v) => (
              <div key={v}>
                <label className="mb-1 block text-xs font-medium">{v}</label>
                <Textarea
                  value={testVars[v] || ''}
                  onChange={(e) => setTestVars({ ...testVars, [v]: e.target.value })}
                  placeholder={`Enter ${v}...`}
                  className="min-h-[60px] font-mono text-xs"
                />
              </div>
            ))}
            {variables.length === 0 && (
              <p className="text-xs text-muted-foreground">No variables defined</p>
            )}
          </div>
        </div>

        {/* Blocks */}
        <div>
          <h4 className="mb-2 text-xs font-medium text-muted-foreground">
            Blocks (enrichment)
          </h4>
          <div className="space-y-2">
            {Object.entries(blocks).map(([b, spec]) => (
              <div key={b}>
                <label className="mb-1 flex items-center gap-2 text-xs font-medium">
                  {b}
                  {spec.optional && (
                    <span className="text-muted-foreground">(optional)</span>
                  )}
                </label>
                <Textarea
                  value={testBlocks[b] || ''}
                  onChange={(e) => setTestBlocks({ ...testBlocks, [b]: e.target.value })}
                  placeholder={spec.default || `Enter ${b}...`}
                  className="min-h-[60px] font-mono text-xs"
                />
              </div>
            ))}
            {Object.keys(blocks).length === 0 && (
              <p className="text-xs text-muted-foreground">No blocks defined</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
