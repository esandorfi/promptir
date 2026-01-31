import { useEffect, useCallback } from 'react'

type KeyHandler = () => void

interface ShortcutConfig {
  key: string
  ctrl?: boolean
  meta?: boolean
  shift?: boolean
  handler: KeyHandler
  description: string
}

const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0

export function useKeyboardShortcuts(shortcuts: ShortcutConfig[]) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      const target = e.target as HTMLElement
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.getAttribute('contenteditable') === 'true' ||
        target.classList.contains('cm-content') // CodeMirror
      ) {
        // Allow Cmd/Ctrl+S even in inputs
        if (!(e.key === 's' && (e.metaKey || e.ctrlKey))) {
          return
        }
      }

      for (const shortcut of shortcuts) {
        const ctrlOrMeta = isMac ? e.metaKey : e.ctrlKey
        const needsCtrl = shortcut.ctrl || shortcut.meta

        if (
          e.key.toLowerCase() === shortcut.key.toLowerCase() &&
          (!needsCtrl || ctrlOrMeta) &&
          (!shortcut.shift || e.shiftKey)
        ) {
          e.preventDefault()
          shortcut.handler()
          return
        }
      }
    },
    [shortcuts]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

// Shortcut display helper
export function formatShortcut(config: Pick<ShortcutConfig, 'key' | 'ctrl' | 'meta' | 'shift'>) {
  const parts: string[] = []

  if (config.ctrl || config.meta) {
    parts.push(isMac ? '⌘' : 'Ctrl')
  }
  if (config.shift) {
    parts.push(isMac ? '⇧' : 'Shift')
  }
  parts.push(config.key.toUpperCase())

  return parts.join(isMac ? '' : '+')
}

// Common shortcuts
export const SHORTCUTS = {
  save: { key: 's', ctrl: true, description: 'Save changes' },
  compile: { key: 'b', ctrl: true, description: 'Compile prompts' },
  newPrompt: { key: 'n', ctrl: true, shift: true, description: 'New prompt' },
  togglePreview: { key: 'p', ctrl: true, description: 'Toggle preview panel' },
  toggleDarkMode: { key: 'd', ctrl: true, shift: true, description: 'Toggle dark mode' },
  escape: { key: 'Escape', description: 'Close modal / Cancel' },
} as const
