import { useQuery } from '@tanstack/react-query'
import * as api from '../api/client'
import { useWorkbenchStore } from '../stores/workbench'

export function useDiff(promptId: string, v1: string, v2: string, enabled: boolean = true) {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useQuery({
    queryKey: ['diff', sessionId, promptId, v1, v2],
    queryFn: () => api.getDiff(sessionId!, promptId, v1, v2),
    enabled: !!sessionId && !!promptId && !!v1 && !!v2 && enabled,
  })
}
