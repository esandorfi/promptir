import { useEffect, useState, useCallback } from 'react'
import { Save, Trash2, GitCompare, AlertTriangle, Loader2 } from 'lucide-react'
import { Button, Badge } from '../ui'
import { TemplateEditor } from './TemplateEditor'
import { MetadataForm } from './MetadataForm'
import { InputsForm } from './InputsForm'
import { TestCaseList } from '../testcases/TestCaseList'
import { VersionDiff } from '../diff/VersionDiff'
import { usePromptSource, useUpdatePrompt, useDeletePrompt } from '../../hooks/usePrompts'
import { useWorkbenchStore } from '../../stores/workbench'
import { parsePromptContent, serializePromptContent, parseSections, cn } from '../../lib/utils'
import { validateTemplate, validateFrontmatter } from '../../lib/validation'
import { formatShortcut, SHORTCUTS } from '../../hooks/useKeyboardShortcuts'
import type { PromptFrontmatter, PromptSection } from '../../types'

const TABS = ['template', 'metadata', 'inputs', 'testcases'] as const

interface PromptEditorProps {
  onSave?: () => void
}

export function PromptEditor({ onSave }: PromptEditorProps) {
  const selectedPrompt = useWorkbenchStore((s) => s.selectedPrompt)
  const activeTab = useWorkbenchStore((s) => s.activeTab)
  const setActiveTab = useWorkbenchStore((s) => s.setActiveTab)
  const isDirty = useWorkbenchStore((s) => s.isDirty)
  const setIsDirty = useWorkbenchStore((s) => s.setIsDirty)
  const draftContent = useWorkbenchStore((s) => s.draftContent)
  const setDraftContent = useWorkbenchStore((s) => s.setDraftContent)
  const setSelectedPrompt = useWorkbenchStore((s) => s.setSelectedPrompt)

  const { data: source, isLoading, error: loadError } = usePromptSource(
    selectedPrompt?.id,
    selectedPrompt?.version
  )
  const updatePrompt = useUpdatePrompt()
  const deletePrompt = useDeletePrompt()

  const [frontmatter, setFrontmatter] = useState<PromptFrontmatter | null>(null)
  const [sections, setSections] = useState<PromptSection[]>([])
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [validationWarnings, setValidationWarnings] = useState<string[]>([])
  const [showDiff, setShowDiff] = useState(false)

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

  // Auto-save draft to localStorage
  useEffect(() => {
    if (!isDirty || !draftContent || !selectedPrompt) return

    const key = `promptir-draft-${selectedPrompt.id}-${selectedPrompt.version}`
    localStorage.setItem(key, draftContent)

    return () => {
      // Cleanup on unmount
    }
  }, [isDirty, draftContent, selectedPrompt])

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
    if (onSave) {
      onSave()
    } else if (selectedPrompt && draftContent) {
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
            // Clear draft from localStorage
            const key = `promptir-draft-${selectedPrompt.id}-${selectedPrompt.version}`
            localStorage.removeItem(key)
          },
        }
      )
    }
  }

  const handleDelete = () => {
    if (!selectedPrompt) return
    if (!confirm(`Delete ${selectedPrompt.id}@${selectedPrompt.version}?`)) return

    deletePrompt.mutate(
      {
        promptId: selectedPrompt.id,
        version: selectedPrompt.version,
      },
      {
        onSuccess: () => {
          setSelectedPrompt(null)
        },
      }
    )
  }

  if (!selectedPrompt) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 text-muted-foreground">
        <p>Select a prompt to edit</p>
        <p className="text-xs">
          Press <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono">?</kbd> for keyboard
          shortcuts
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading...
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 text-destructive">
        <AlertTriangle className="h-6 w-6" />
        <p>Failed to load prompt</p>
        <p className="text-xs text-muted-foreground">{loadError.message}</p>
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
          {updatePrompt.isPending && (
            <Badge variant="outline">
              <Loader2 className="mr-1 h-3 w-3 animate-spin" />
              Saving...
            </Badge>
          )}
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
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDiff(true)}
            title="Compare versions"
          >
            <GitCompare className="mr-1.5 h-3.5 w-3.5" />
            Diff
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={!isDirty || updatePrompt.isPending}
            title={`Save (${formatShortcut(SHORTCUTS.save)})`}
          >
            <Save className="mr-1.5 h-3.5 w-3.5" />
            Save
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDelete}
            disabled={deletePrompt.isPending}
            title="Delete prompt"
          >
            {deletePrompt.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4 text-destructive" />
            )}
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
              <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
              {e}
            </div>
          ))}
          {validationWarnings.map((w, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-amber-600">
              <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
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
          <TestCaseList promptId={selectedPrompt.id} version={selectedPrompt.version} />
        )}
      </div>

      {/* Diff modal */}
      {showDiff && (
        <VersionDiff
          promptId={selectedPrompt.id}
          currentVersion={selectedPrompt.version}
          onClose={() => setShowDiff(false)}
        />
      )}
    </div>
  )
}
