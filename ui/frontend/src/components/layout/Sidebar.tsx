import { ChevronRight, FileText, Plus, FolderOpen } from 'lucide-react'
import { useState } from 'react'
import { cn } from '../../lib/utils'
import { Button } from '../ui'
import { usePrompts } from '../../hooks/usePrompts'
import { useWorkbenchStore } from '../../stores/workbench'
import type { PromptSummary } from '../../types'

export function Sidebar() {
  const { data, isLoading } = usePrompts()
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const selectedPrompt = useWorkbenchStore((s) => s.selectedPrompt)
  const setSelectedPrompt = useWorkbenchStore((s) => s.setSelectedPrompt)
  const [expandedPrompts, setExpandedPrompts] = useState<Set<string>>(new Set())
  const [showIncludes, setShowIncludes] = useState(false)

  if (!sessionId) {
    return (
      <aside className="flex w-56 flex-col border-r border-border bg-muted/30">
        <div className="flex flex-1 items-center justify-center p-4 text-sm text-muted-foreground">
          Select a session to start
        </div>
      </aside>
    )
  }

  if (isLoading) {
    return (
      <aside className="flex w-56 flex-col border-r border-border bg-muted/30">
        <div className="flex flex-1 items-center justify-center p-4 text-sm text-muted-foreground">
          Loading...
        </div>
      </aside>
    )
  }

  // Group prompts by id
  const promptGroups = (data?.prompts || []).reduce(
    (acc, p) => {
      if (!acc[p.id]) acc[p.id] = []
      acc[p.id].push(p)
      return acc
    },
    {} as Record<string, PromptSummary[]>
  )

  const toggleExpanded = (id: string) => {
    setExpandedPrompts((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <aside className="flex w-56 flex-col border-r border-border bg-muted/30">
      {/* Prompts section */}
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="text-xs font-medium uppercase text-muted-foreground">Prompts</span>
        <Button variant="ghost" size="icon" className="h-6 w-6">
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {Object.entries(promptGroups).map(([id, versions]) => {
          const isExpanded = expandedPrompts.has(id) || versions.length === 1
          const hasMultiple = versions.length > 1

          return (
            <div key={id} className="mb-1">
              <button
                onClick={() => {
                  if (hasMultiple) {
                    toggleExpanded(id)
                  } else {
                    setSelectedPrompt({ id, version: versions[0].version })
                  }
                }}
                className={cn(
                  'flex w-full items-center gap-1.5 rounded px-2 py-1 text-left text-sm',
                  'hover:bg-accent',
                  selectedPrompt?.id === id && !hasMultiple && 'bg-accent'
                )}
              >
                {hasMultiple ? (
                  <ChevronRight
                    className={cn(
                      'h-3.5 w-3.5 text-muted-foreground transition-transform',
                      isExpanded && 'rotate-90'
                    )}
                  />
                ) : (
                  <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                )}
                <span className="truncate">{id}</span>
                {hasMultiple && (
                  <span className="ml-auto text-xs text-muted-foreground">
                    {versions.length}
                  </span>
                )}
              </button>

              {hasMultiple && isExpanded && (
                <div className="ml-4 border-l border-border pl-2">
                  {versions
                    .sort((a, b) => b.version.localeCompare(a.version))
                    .map((v) => (
                      <button
                        key={v.version}
                        onClick={() => setSelectedPrompt({ id, version: v.version })}
                        className={cn(
                          'flex w-full items-center gap-1.5 rounded px-2 py-1 text-left text-sm',
                          'hover:bg-accent',
                          selectedPrompt?.id === id &&
                            selectedPrompt?.version === v.version &&
                            'bg-accent'
                        )}
                      >
                        <FileText className="h-3 w-3 text-muted-foreground" />
                        <span className="text-muted-foreground">{v.version}</span>
                      </button>
                    ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Includes section */}
      {(data?.includes?.length ?? 0) > 0 && (
        <>
          <button
            onClick={() => setShowIncludes(!showIncludes)}
            className="flex items-center gap-1.5 border-t border-border px-3 py-2 text-xs font-medium uppercase text-muted-foreground hover:bg-accent"
          >
            <ChevronRight
              className={cn(
                'h-3 w-3 transition-transform',
                showIncludes && 'rotate-90'
              )}
            />
            <FolderOpen className="h-3 w-3" />
            Includes
          </button>

          {showIncludes && (
            <div className="max-h-40 overflow-y-auto border-t border-border p-2">
              {data?.includes.map((inc) => (
                <button
                  key={`${inc.id}@${inc.version}`}
                  onClick={() => setSelectedPrompt({ id: inc.id, version: inc.version })}
                  className={cn(
                    'flex w-full items-center gap-1.5 rounded px-2 py-1 text-left text-sm',
                    'hover:bg-accent',
                    selectedPrompt?.id === inc.id &&
                      selectedPrompt?.version === inc.version &&
                      'bg-accent'
                  )}
                >
                  <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="truncate text-muted-foreground">
                    {inc.id}@{inc.version}
                  </span>
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </aside>
  )
}
