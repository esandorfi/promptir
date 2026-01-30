import { Play, Moon, Sun, Keyboard, Save } from 'lucide-react'
import { Button, Select, Badge } from '../ui'
import { useSessions } from '../../hooks/useSession'
import { useCompile } from '../../hooks/usePrompts'
import { useWorkbenchStore } from '../../stores/workbench'
import { useDarkMode } from '../../hooks/useDarkMode'
import { formatShortcut, SHORTCUTS } from '../../hooks/useKeyboardShortcuts'

interface HeaderProps {
  onSave?: () => void
  onCompile?: () => void
}

export function Header({ onSave, onCompile }: HeaderProps) {
  const { data: sessions, isLoading } = useSessions()
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const setSessionId = useWorkbenchStore((s) => s.setSessionId)
  const isDirty = useWorkbenchStore((s) => s.isDirty)
  const compile = useCompile()
  const { isDark, toggle: toggleDarkMode } = useDarkMode()

  const handleCompile = () => {
    if (onCompile) {
      onCompile()
    } else if (sessionId) {
      compile.mutate()
    }
  }

  return (
    <header className="flex h-12 items-center justify-between border-b border-border px-4">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-semibold tracking-tight">promptir</h1>

        <Select
          value={sessionId || ''}
          onChange={(e) => setSessionId(e.target.value)}
          className="w-48"
          disabled={isLoading}
        >
          <option value="" disabled>
            Select session...
          </option>
          {sessions?.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </Select>

        {isDirty && <Badge variant="secondary">Unsaved</Badge>}
      </div>

      <div className="flex items-center gap-1">
        {/* Save button */}
        {onSave && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onSave}
            disabled={!isDirty}
            title={`Save (${formatShortcut(SHORTCUTS.save)})`}
          >
            <Save className="mr-1.5 h-3.5 w-3.5" />
            Save
          </Button>
        )}

        {/* Compile button */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleCompile}
          disabled={!sessionId || compile.isPending}
          title={`Compile (${formatShortcut(SHORTCUTS.compile)})`}
        >
          <Play className="mr-1.5 h-3.5 w-3.5" />
          {compile.isPending ? 'Compiling...' : 'Compile'}
        </Button>

        {/* Dark mode toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleDarkMode}
          title={`Toggle dark mode (${formatShortcut(SHORTCUTS.toggleDarkMode)})`}
        >
          {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>

        {/* Keyboard shortcuts hint */}
        <Button variant="ghost" size="icon" title="Keyboard shortcuts (Shift+?)">
          <Keyboard className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
