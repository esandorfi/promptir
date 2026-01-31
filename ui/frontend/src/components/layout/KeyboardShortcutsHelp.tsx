import { X } from 'lucide-react'
import { Button } from '../ui'
import { formatShortcut, SHORTCUTS } from '../../hooks/useKeyboardShortcuts'

interface KeyboardShortcutsHelpProps {
  onClose: () => void
}

export function KeyboardShortcutsHelp({ onClose }: KeyboardShortcutsHelpProps) {
  const shortcuts = [
    { ...SHORTCUTS.save, description: 'Save changes' },
    { ...SHORTCUTS.compile, description: 'Compile prompts' },
    { ...SHORTCUTS.togglePreview, description: 'Toggle preview panel' },
    { ...SHORTCUTS.toggleDarkMode, description: 'Toggle dark mode' },
    { key: '?', shift: true, description: 'Show this help' },
    { ...SHORTCUTS.escape, description: 'Close modal' },
  ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-lg border border-border bg-background p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Keyboard Shortcuts</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-2">
          {shortcuts.map((shortcut, i) => (
            <div key={i} className="flex items-center justify-between py-1">
              <span className="text-sm text-muted-foreground">{shortcut.description}</span>
              <kbd className="rounded bg-muted px-2 py-1 font-mono text-xs">
                {formatShortcut(shortcut)}
              </kbd>
            </div>
          ))}
        </div>

        <p className="mt-4 text-xs text-muted-foreground">
          Press <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono">?</kbd> to show this help
          at any time.
        </p>
      </div>
    </div>
  )
}
