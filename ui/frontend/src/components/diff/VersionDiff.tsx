import { useState } from 'react'
import { X } from 'lucide-react'
import { Button, Select } from '../ui'
import { useDiff } from '../../hooks/useDiff'
import { usePrompts } from '../../hooks/usePrompts'
import { cn } from '../../lib/utils'

interface VersionDiffProps {
  promptId: string
  currentVersion: string
  onClose: () => void
}

export function VersionDiff({ promptId, currentVersion, onClose }: VersionDiffProps) {
  const { data: promptsData } = usePrompts()
  const [v1, setV1] = useState(currentVersion)
  const [v2, setV2] = useState('')

  // Get all versions for this prompt
  const versions =
    promptsData?.prompts
      .filter((p) => p.id === promptId)
      .map((p) => p.version)
      .sort()
      .reverse() || []

  const { data: diff, isLoading, error } = useDiff(promptId, v1, v2, !!v1 && !!v2)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="flex h-[80vh] w-[80vw] max-w-4xl flex-col rounded-lg border border-border bg-background shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-sm font-medium">
            Diff: {promptId}
          </h2>
          <div className="flex items-center gap-3">
            <Select value={v1} onChange={(e) => setV1(e.target.value)} className="w-24">
              {versions.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </Select>
            <span className="text-muted-foreground">→</span>
            <Select value={v2} onChange={(e) => setV2(e.target.value)} className="w-24">
              <option value="">Select...</option>
              {versions
                .filter((v) => v !== v1)
                .map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
            </Select>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {!v2 && (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              Select a version to compare
            </div>
          )}

          {isLoading && (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              Loading diff...
            </div>
          )}

          {error && (
            <div className="rounded border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
              {error.message}
            </div>
          )}

          {diff && (
            <div className="space-y-4">
              {/* Frontmatter diff */}
              {diff.frontmatter_diff && (
                <div>
                  <h3 className="mb-2 text-xs font-medium text-muted-foreground">
                    Frontmatter Changes
                  </h3>
                  <DiffBlock content={diff.frontmatter_diff} />
                </div>
              )}

              {/* Template diff */}
              {diff.template_diff && (
                <div>
                  <h3 className="mb-2 text-xs font-medium text-muted-foreground">
                    Template Changes
                  </h3>
                  <DiffBlock content={diff.template_diff} />
                </div>
              )}

              {!diff.frontmatter_diff && !diff.template_diff && (
                <div className="text-center text-muted-foreground">
                  No differences found
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function DiffBlock({ content }: { content: string }) {
  const lines = content.split('\n')

  return (
    <div className="overflow-x-auto rounded border border-border bg-muted/30 font-mono text-xs">
      {lines.map((line, i) => (
        <div
          key={i}
          className={cn(
            'whitespace-pre px-3 py-0.5',
            line.startsWith('+') && !line.startsWith('+++') && 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300',
            line.startsWith('-') && !line.startsWith('---') && 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300',
            line.startsWith('@@') && 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
          )}
        >
          {line}
        </div>
      ))}
    </div>
  )
}
