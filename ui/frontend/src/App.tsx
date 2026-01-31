import { useState, useCallback } from 'react'
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { PromptEditor } from './components/prompts/PromptEditor'
import { PreviewPanel } from './components/preview/PreviewPanel'
import { KeyboardShortcutsHelp } from './components/layout/KeyboardShortcutsHelp'
import { usePromptDetail, useUpdatePrompt, useCompile } from './hooks/usePrompts'
import { useWorkbenchStore } from './stores/workbench'
import { useKeyboardShortcuts, SHORTCUTS } from './hooks/useKeyboardShortcuts'
import { useDarkMode } from './hooks/useDarkMode'

export default function App() {
  const selectedPrompt = useWorkbenchStore((s) => s.selectedPrompt)
  const isDirty = useWorkbenchStore((s) => s.isDirty)
  const draftContent = useWorkbenchStore((s) => s.draftContent)
  const setIsDirty = useWorkbenchStore((s) => s.setIsDirty)
  const setDraftContent = useWorkbenchStore((s) => s.setDraftContent)
  const previewExpanded = useWorkbenchStore((s) => s.previewExpanded)
  const setPreviewExpanded = useWorkbenchStore((s) => s.setPreviewExpanded)
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  const [showShortcuts, setShowShortcuts] = useState(false)

  const { data: promptDetail } = usePromptDetail(selectedPrompt?.id, selectedPrompt?.version)
  const updatePrompt = useUpdatePrompt()
  const compile = useCompile()
  const { toggle: toggleDarkMode } = useDarkMode()

  // Save handler
  const handleSave = useCallback(() => {
    if (!selectedPrompt || !draftContent || !isDirty) return

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
  }, [selectedPrompt, draftContent, isDirty, updatePrompt, setIsDirty, setDraftContent])

  // Compile handler
  const handleCompile = useCallback(() => {
    if (sessionId) {
      compile.mutate()
    }
  }, [sessionId, compile])

  // Keyboard shortcuts
  useKeyboardShortcuts([
    { ...SHORTCUTS.save, handler: handleSave },
    { ...SHORTCUTS.compile, handler: handleCompile },
    { ...SHORTCUTS.togglePreview, handler: () => setPreviewExpanded(!previewExpanded) },
    { ...SHORTCUTS.toggleDarkMode, handler: toggleDarkMode },
    { key: '?', shift: true, handler: () => setShowShortcuts(true), description: 'Show shortcuts' },
    { ...SHORTCUTS.escape, handler: () => setShowShortcuts(false) },
  ])

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background text-foreground">
      <Header onSave={handleSave} onCompile={handleCompile} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />

        <main className="flex flex-1 flex-col overflow-hidden">
          <PromptEditor onSave={handleSave} />
          <PreviewPanel prompt={promptDetail} />
        </main>
      </div>

      {showShortcuts && <KeyboardShortcutsHelp onClose={() => setShowShortcuts(false)} />}
    </div>
  )
}
