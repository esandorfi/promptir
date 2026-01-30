import { useCallback } from 'react'
import { Plus, X } from 'lucide-react'
import { Input, Button, Badge } from '../ui'
import type { PromptFrontmatter, BlockSpec } from '../../types'

interface InputsFormProps {
  frontmatter: PromptFrontmatter
  onChange: (frontmatter: PromptFrontmatter) => void
}

export function InputsForm({ frontmatter, onChange }: InputsFormProps) {
  // Variables
  const handleAddVariable = useCallback(() => {
    const name = prompt('Variable name (lowercase, no underscore prefix):')
    if (name) {
      const variables = [...(frontmatter.variables || []), name]
      onChange({ ...frontmatter, variables })
    }
  }, [frontmatter, onChange])

  const handleRemoveVariable = useCallback(
    (variable: string) => {
      const variables = (frontmatter.variables || []).filter((v) => v !== variable)
      onChange({ ...frontmatter, variables })
    },
    [frontmatter, onChange]
  )

  // Blocks
  const handleAddBlock = useCallback(() => {
    const name = prompt('Block name (must start with underscore, e.g., _rag_context):')
    if (name) {
      const blocks = {
        ...(frontmatter.blocks || {}),
        [name]: { optional: true, default: '' },
      }
      onChange({ ...frontmatter, blocks })
    }
  }, [frontmatter, onChange])

  const handleRemoveBlock = useCallback(
    (block: string) => {
      const blocks = { ...(frontmatter.blocks || {}) }
      delete blocks[block]
      onChange({ ...frontmatter, blocks })
    },
    [frontmatter, onChange]
  )

  const handleBlockChange = useCallback(
    (block: string, spec: BlockSpec) => {
      const blocks = { ...(frontmatter.blocks || {}), [block]: spec }
      onChange({ ...frontmatter, blocks })
    },
    [frontmatter, onChange]
  )

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="mx-auto max-w-2xl space-y-6">
        {/* Variables */}
        <section>
          <h3 className="mb-1 text-sm font-medium">Variables</h3>
          <p className="mb-3 text-xs text-muted-foreground">
            Required inputs that must be provided at runtime
          </p>

          <div className="space-y-2">
            {(frontmatter.variables || []).map((variable) => (
              <div
                key={variable}
                className="flex items-center gap-2 rounded border border-border bg-background p-2"
              >
                <code className="flex-1 font-mono text-sm">{variable}</code>
                <Badge variant="secondary">required</Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => handleRemoveVariable(variable)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}

            <Button variant="outline" size="sm" onClick={handleAddVariable}>
              <Plus className="mr-1 h-3 w-3" />
              Add Variable
            </Button>
          </div>
        </section>

        {/* Blocks */}
        <section>
          <h3 className="mb-1 text-sm font-medium">Blocks (Enrichment Slots)</h3>
          <p className="mb-3 text-xs text-muted-foreground">
            Optional slots that can be filled by enrichment pipelines (RAG, tools, etc.)
          </p>

          <div className="space-y-2">
            {Object.entries(frontmatter.blocks || {}).map(([block, spec]) => (
              <div
                key={block}
                className="rounded border border-border bg-background p-3"
              >
                <div className="flex items-center gap-2">
                  <code className="flex-1 font-mono text-sm">{block}</code>
                  <label className="flex items-center gap-1.5 text-xs">
                    <input
                      type="checkbox"
                      checked={spec.optional}
                      onChange={(e) =>
                        handleBlockChange(block, { ...spec, optional: e.target.checked })
                      }
                      className="h-3.5 w-3.5"
                    />
                    optional
                  </label>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => handleRemoveBlock(block)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {spec.optional && (
                  <div className="mt-2">
                    <label className="mb-1 block text-xs text-muted-foreground">
                      Default value
                    </label>
                    <Input
                      value={spec.default}
                      onChange={(e) =>
                        handleBlockChange(block, { ...spec, default: e.target.value })
                      }
                      placeholder="(empty)"
                      className="font-mono text-xs"
                    />
                  </div>
                )}
              </div>
            ))}

            <Button variant="outline" size="sm" onClick={handleAddBlock}>
              <Plus className="mr-1 h-3 w-3" />
              Add Block
            </Button>
          </div>
        </section>

        {/* Summary */}
        <section className="rounded border border-border bg-muted/30 p-3">
          <h4 className="mb-2 text-xs font-medium text-muted-foreground">Summary</h4>
          <div className="text-sm">
            <span className="font-medium">{(frontmatter.variables || []).length}</span>{' '}
            required variables,{' '}
            <span className="font-medium">
              {Object.keys(frontmatter.blocks || {}).length}
            </span>{' '}
            enrichment blocks
          </div>
        </section>
      </div>
    </div>
  )
}
