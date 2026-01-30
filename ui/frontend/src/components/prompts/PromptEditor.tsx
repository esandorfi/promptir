import { useEffect, useState, useCallback } from 'react'
import { Save, Trash2, GitCompare, AlertTriangle } from 'lucide-react'
import { Button, Badge } from '../ui'
import { TemplateEditor } from './TemplateEditor'
import { MetadataForm } from './MetadataForm'
import { InputsForm } from './InputsForm'
import { usePromptSource, useUpdatePrompt, useDeletePrompt } from '../../hooks/usePrompts'
import { useWorkbenchStore } from '../../stores/workbench'
import { parsePromptContent, serializePromptContent, parseSections, cn } from '../../lib/utils'
import { validateTemplate, validateFrontmatter } from '../../lib/validation'
import type { PromptFrontmatter, PromptSection } from '../../types'

const TABS = ['template', 'metadata', 'inputs', 'testcases'] as const

export function PromptEditor() {
  const selectedPrompt = useWorkbenchStore((s) => s.selectedPrompt)
  const activeTab = useWorkbenchStore((s) => s.activeTab)
  const setActiveTab = useWorkbenchStore((s) => s.setActiveTab)
  const isDirty = useWorkbenchStore((s) => s.isDirty)
  const setIsDirty = useWorkbenchStore((s) => s.setIsDirty)
  const draftContent = useWorkbenchStore((s) => s.draftContent)
  const setDraftContent = useWorkbenchStore((s) => s.setDraftContent)

  const { data: source, isLoading } = usePromptSource(
    selectedPrompt?.id,
    selectedPrompt?.version
  )
  const updatePrompt = useUpdatePrompt()
  const deletePrompt = useDeletePrompt()

  const [frontmatter, setFrontmatter] = useState<PromptFrontmatter | null>(null)
  const [sections, setSections] = useState<PromptSection[]>([])
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [validationWarnings, setValidationWarnings] = useState<string[]>([])

  // Parse source when loaded
  useEffect(() => {
    if (source) {
      const content = draftContent ?? source.content
      const { frontmatter: fm, body } = parsePromptContent(content)
      setFrontmatter(fm as PromptFrontmatter | null)
      setSections(parseSections(body))
      validateAndSetErrors(fm, body)
    }
  }, [source, draftContent])

  // Auto-save draft
  useEffect(() => {
    if (!isDirty || !draftContent) return

    const timer = setTimeout(() => {
      // Auto-save to localStorage could go here
    }, 1000)

    return () => clearTimeout(timer)
  }, [isDirty, draftContent])

  const validateAndSetErrors = useCallback(
    (fm: Record<string, unknown> | null, body: string) => {
      const errors: string[] = []
      const warnings: string[] = []

      if (fm) {
        const fmValidation = validateFrontmatter(fm)
        errors.push(...fmValidation.errors.map((e) => e.message))
        warnings.push(...fmValidation.warnings.map((w) => w.message))

        const templateValidation = validateTemplate(
          body,
          (fm.variables as string[]) || [],
          (fm.blocks as Record<string, unknown>) || {},
          (fm.template_engine as string) || 'simple'
        )
        errors.push(...templateValidation.errors.map((e) => e.message))
        warnings.push(...templateValidation.warnings.map((w) => w.message))
      }

      setValidationErrors(errors)
      setValidationWarnings(warnings)
    },
    []
  )

  const handleContentChange = useCallback(
    (newContent: string) => {
      setDraftContent(newContent)
      const { frontmatter: fm, body } = parsePromptContent(newContent)
      setFrontmatter(fm as PromptFrontmatter | null)
      setSections(parseSections(body))
      validateAndSetErrors(fm, body)
    },
    [setDraftContent, validateAndSetErrors]
  )

  const handleFrontmatterChange = useCallback(
    (newFm: PromptFrontmatter) => {
      setFrontmatter(newFm)
      const body = sections.map((s) => `# ${s.role}\n${s.content}`).join('\n\n')
      const newContent = serializePromptContent(newFm, body)
      setDraftContent(newContent)
      validateAndSetErrors(newFm, body)
    },
    [sections, setDraftContent, validateAndSetErrors]
  )

  const handleSectionsChange = useCallback(
    (newSections: PromptSection[]) => {
      setSections(newSections)
      if (frontmatter) {
        const body = newSections.map((s) => `# ${s.role}\n${s.content}`).join('\n\n')
        const newContent = serializePromptContent(frontmatter, body)
        setDraftContent(newContent)
        validateAndSetErrors(frontmatter, body)
      }
    },
    [frontmatter, setDraftContent, validateAndSetErrors]
  )

  const handleSave = () => {
    if (!selectedPrompt || !draftContent) return

    updatePrompt.mutate(
      {
        promptId: selectedPrompt.id,
        version: selectedPrompt.version,
        content: draftContent,
      },
      {
        onSuccess: () => {
          setIsDirty(false)
          setDraftContent(null)
        },
      }
    )
  }

  const handleDelete = () => {
    if (!selectedPrompt) return
    if (!confirm(`Delete ${selectedPrompt.id}@${selectedPrompt.version}?`)) return

    deletePrompt.mutate({
      promptId: selectedPrompt.id,
      version: selectedPrompt.version,
    })
  }

  if (!selectedPrompt) {
    return (
      <div className="flex flex-1 items-center justify-center text-muted-foreground">
        Select a prompt to edit
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center text-muted-foreground">
        Loading...
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="font-medium">
            {selectedPrompt.id}@{selectedPrompt.version}
          </span>
          {isDirty && <Badge variant="secondary">Unsaved</Badge>}
          {validationErrors.length > 0 && (
            <Badge variant="destructive">{validationErrors.length} errors</Badge>
          )}
          {validationWarnings.length > 0 && (
            <Badge variant="outline" className="text-amber-600">
              {validationWarnings.length} warnings
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <GitCompare className="mr-1.5 h-3.5 w-3.5" />
            Diff
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={!isDirty || updatePrompt.isPending}
          >
            <Save className="mr-1.5 h-3.5 w-3.5" />
            {updatePrompt.isPending ? 'Saving...' : 'Save'}
          </Button>
          <Button variant="ghost" size="icon" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              'px-4 py-2 text-sm font-medium capitalize',
              'border-b-2 transition-colors',
              activeTab === tab
                ? 'border-foreground text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Validation warnings */}
      {(validationErrors.length > 0 || validationWarnings.length > 0) && (
        <div className="border-b border-border bg-amber-50 px-4 py-2 dark:bg-amber-950/20">
          {validationErrors.map((e, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-destructive">
              <AlertTriangle className="h-3.5 w-3.5" />
              {e}
            </div>
          ))}
          {validationWarnings.map((w, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-amber-600">
              <AlertTriangle className="h-3.5 w-3.5" />
              {w}
            </div>
          ))}
        </div>
      )}

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'template' && (
          <TemplateEditor
            sections={sections}
            onChange={handleSectionsChange}
            variables={frontmatter?.variables || []}
            blocks={Object.keys(frontmatter?.blocks || {})}
            templateEngine={frontmatter?.template_engine || 'simple'}
          />
        )}
        {activeTab === 'metadata' && frontmatter && (
          <MetadataForm frontmatter={frontmatter} onChange={handleFrontmatterChange} />
        )}
        {activeTab === 'inputs' && frontmatter && (
          <InputsForm frontmatter={frontmatter} onChange={handleFrontmatterChange} />
        )}
        {activeTab === 'testcases' && (
          <div className="p-4 text-muted-foreground">Test cases coming soon...</div>
        )}
      </div>
    </div>
  )
}
