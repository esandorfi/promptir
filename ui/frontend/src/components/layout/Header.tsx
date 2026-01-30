import { Settings, Play } from 'lucide-react'
import { Button, Select } from '../ui'
import { useSessions } from '../../hooks/useSession'
import { useCompile } from '../../hooks/usePrompts'
import { useWorkbenchStore } from '../../stores/workbench'

export function Header() {
  const { data: sessions, isLoading } = useSessions()
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const setSessionId = useWorkbenchStore((s) => s.setSessionId)
  const compile = useCompile()

  const handleCompile = () => {
    if (sessionId) {
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
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleCompile}
          disabled={!sessionId || compile.isPending}
        >
          <Play className="mr-1.5 h-3.5 w-3.5" />
          {compile.isPending ? 'Compiling...' : 'Compile'}
        </Button>

        <Button variant="ghost" size="icon">
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
