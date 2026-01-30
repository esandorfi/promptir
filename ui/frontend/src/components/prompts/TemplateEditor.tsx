import { useCallback } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { Plus, Trash2 } from 'lucide-react'
import { Button, Select } from '../ui'
import { createEditorExtensions } from '../../lib/codemirror/setup'
import type { PromptSection } from '../../types'

interface TemplateEditorProps {
  sections: PromptSection[]
  onChange: (sections: PromptSection[]) => void
  variables: string[]
  blocks: string[]
  templateEngine: string
}

const ROLES = ['system', 'user', 'assistant']

export function TemplateEditor({
  sections,
  onChange,
  variables,
  blocks,
  templateEngine,
}: TemplateEditorProps) {
  const extensions = createEditorExtensions({
    variables,
    blocks,
  })

  const handleSectionChange = useCallback(
    (index: number, content: string) => {
      const newSections = [...sections]
      newSections[index] = { ...newSections[index], content }
      onChange(newSections)
    },
    [sections, onChange]
  )

  const handleRoleChange = useCallback(
    (index: number, role: string) => {
      const newSections = [...sections]
      newSections[index] = { ...newSections[index], role }
      onChange(newSections)
    },
    [sections, onChange]
  )

  const handleAddSection = useCallback(() => {
    const usedRoles = new Set(sections.map((s) => s.role))
    const availableRole = ROLES.find((r) => !usedRoles.has(r)) || 'user'
    onChange([...sections, { role: availableRole, content: '' }])
  }, [sections, onChange])

  const handleRemoveSection = useCallback(
    (index: number) => {
      const newSections = sections.filter((_, i) => i !== index)
      onChange(newSections)
    },
    [sections, onChange]
  )

  // If no sections, show a placeholder
  if (sections.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 p-8">
        <p className="text-muted-foreground">No template sections defined</p>
        <Button onClick={handleAddSection}>
          <Plus className="mr-1.5 h-4 w-4" />
          Add Section
        </Button>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        {sections.map((section, index) => (
          <div key={index} className="border-b border-border">
            {/* Section header */}
            <div className="flex items-center gap-2 bg-muted/50 px-3 py-1.5">
              <Select
                value={section.role}
                onChange={(e) => handleRoleChange(index, e.target.value)}
                className="h-7 w-28 text-xs"
              >
                {ROLES.map((role) => (
                  <option key={role} value={role}>
                    # {role}
                  </option>
                ))}
              </Select>

              <div className="flex-1" />

              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => handleRemoveSection(index)}
                disabled={sections.length === 1}
              >
                <Trash2 className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
            </div>

            {/* Section editor */}
            <div className="min-h-[120px]">
              <CodeMirror
                value={section.content}
                onChange={(value) => handleSectionChange(index, value)}
                extensions={extensions}
                basicSetup={false}
                className="text-sm"
              />
            </div>
          </div>
        ))}
      </div>

      {/* Add section button */}
      <div className="border-t border-border p-2">
        <Button variant="outline" size="sm" onClick={handleAddSection} className="w-full">
          <Plus className="mr-1.5 h-3.5 w-3.5" />
          Add Section
        </Button>
      </div>

      {/* Template engine indicator */}
      <div className="border-t border-border bg-muted/30 px-3 py-1.5 text-xs text-muted-foreground">
        Template engine: <span className="font-medium">{templateEngine}</span>
        {templateEngine === 'jinja2_sandbox' && (
          <span className="ml-2">(supports conditionals, loops)</span>
        )}
      </div>
    </div>
  )
}
