import { useCallback } from 'react'
import { Plus, X } from 'lucide-react'
import { Input, Select, Button, Badge } from '../ui'
import type { PromptFrontmatter } from '../../types'

interface MetadataFormProps {
  frontmatter: PromptFrontmatter
  onChange: (frontmatter: PromptFrontmatter) => void
}

export function MetadataForm({ frontmatter, onChange }: MetadataFormProps) {
  const handleChange = useCallback(
    (field: keyof PromptFrontmatter, value: unknown) => {
      onChange({ ...frontmatter, [field]: value })
    },
    [frontmatter, onChange]
  )

  const handleMetadataChange = useCallback(
    (key: string, value: string) => {
      const metadata = { ...(frontmatter.metadata || {}), [key]: value }
      onChange({ ...frontmatter, metadata })
    },
    [frontmatter, onChange]
  )

  const handleRemoveMetadata = useCallback(
    (key: string) => {
      const metadata = { ...(frontmatter.metadata || {}) }
      delete metadata[key]
      onChange({ ...frontmatter, metadata })
    },
    [frontmatter, onChange]
  )

  const handleAddMetadata = useCallback(() => {
    const key = prompt('Metadata key:')
    if (key) {
      handleMetadataChange(key, '')
    }
  }, [handleMetadataChange])

  const handleIncludeRemove = useCallback(
    (include: string) => {
      const includes = (frontmatter.includes || []).filter((i) => i !== include)
      onChange({ ...frontmatter, includes })
    },
    [frontmatter, onChange]
  )

  const handleIncludeAdd = useCallback(() => {
    const include = prompt('Include reference (e.g., policy@v3):')
    if (include) {
      const includes = [...(frontmatter.includes || []), include]
      onChange({ ...frontmatter, includes })
    }
  }, [frontmatter, onChange])

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="mx-auto max-w-2xl space-y-6">
        {/* Core fields */}
        <section>
          <h3 className="mb-3 text-sm font-medium">Identity</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">ID</label>
              <Input
                value={frontmatter.id}
                onChange={(e) => handleChange('id', e.target.value)}
                placeholder="prompt_id"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Version</label>
              <Input
                value={frontmatter.version}
                onChange={(e) => handleChange('version', e.target.value)}
                placeholder="v1"
              />
            </div>
          </div>
        </section>

        {/* Template engine */}
        <section>
          <h3 className="mb-3 text-sm font-medium">Template Engine</h3>
          <Select
            value={frontmatter.template_engine || 'simple'}
            onChange={(e) => handleChange('template_engine', e.target.value)}
            className="w-48"
          >
            <option value="simple">simple (&#123;&#123;var&#125;&#125;)</option>
            <option value="jinja2_sandbox">jinja2_sandbox (full Jinja2)</option>
          </Select>
          <p className="mt-1 text-xs text-muted-foreground">
            {frontmatter.template_engine === 'jinja2_sandbox'
              ? 'Supports conditionals, loops, and filters'
              : 'Simple variable substitution only'}
          </p>
        </section>

        {/* Includes */}
        <section>
          <h3 className="mb-3 text-sm font-medium">Includes</h3>
          <div className="flex flex-wrap gap-2">
            {(frontmatter.includes || []).map((include) => (
              <Badge key={include} variant="secondary" className="gap-1 pr-1">
                {include}
                <button
                  onClick={() => handleIncludeRemove(include)}
                  className="ml-1 rounded-full p-0.5 hover:bg-foreground/10"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
            <Button variant="outline" size="sm" onClick={handleIncludeAdd}>
              <Plus className="mr-1 h-3 w-3" />
              Add Include
            </Button>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Reference reusable content from _includes/
          </p>
        </section>

        {/* Custom metadata */}
        <section>
          <h3 className="mb-3 text-sm font-medium">Custom Metadata</h3>
          <div className="space-y-2">
            {Object.entries(frontmatter.metadata || {}).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2">
                <Input value={key} disabled className="w-32 bg-muted" />
                <Input
                  value={String(value)}
                  onChange={(e) => handleMetadataChange(key, e.target.value)}
                  className="flex-1"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleRemoveMetadata(key)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button variant="outline" size="sm" onClick={handleAddMetadata}>
              <Plus className="mr-1 h-3 w-3" />
              Add Metadata
            </Button>
          </div>
        </section>
      </div>
    </div>
  )
}
