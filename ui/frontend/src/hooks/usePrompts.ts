import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api/client'
import { useWorkbenchStore } from '../stores/workbench'

export function usePrompts() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useQuery({
    queryKey: ['prompts', sessionId],
    queryFn: () => api.getPrompts(sessionId!),
    enabled: !!sessionId,
  })
}

export function usePromptDetail(promptId: string | undefined, version: string | undefined) {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useQuery({
    queryKey: ['prompt', sessionId, promptId, version],
    queryFn: () => api.getPrompt(sessionId!, promptId!, version),
    enabled: !!sessionId && !!promptId,
  })
}

export function usePromptSource(promptId: string | undefined, version: string | undefined) {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useQuery({
    queryKey: ['promptSource', sessionId, promptId, version],
    queryFn: () => api.getPromptSource(sessionId!, promptId!, version!),
    enabled: !!sessionId && !!promptId && !!version,
  })
}

export function useUpdatePrompt() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      promptId,
      version,
      content,
    }: {
      promptId: string
      version: string
      content: string
    }) => api.updatePrompt(sessionId!, promptId, version, content),
    onSuccess: (_, { promptId, version }) => {
      queryClient.invalidateQueries({ queryKey: ['promptSource', sessionId, promptId, version] })
      queryClient.invalidateQueries({ queryKey: ['prompt', sessionId, promptId, version] })
      queryClient.invalidateQueries({ queryKey: ['prompts', sessionId] })
    },
  })
}

export function useCreatePrompt() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, version, content }: { id: string; version: string; content: string }) =>
      api.createPrompt(sessionId!, id, version, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts', sessionId] })
    },
  })
}

export function useDeletePrompt() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ promptId, version }: { promptId: string; version: string }) =>
      api.deletePrompt(sessionId!, promptId, version),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts', sessionId] })
    },
  })
}

export function useCompile() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.compileSession(sessionId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts', sessionId] })
    },
  })
}

export function useValidate() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useMutation({
    mutationFn: () => api.validateSession(sessionId!),
  })
}

export function useRender() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useMutation({
    mutationFn: (request: Parameters<typeof api.renderPrompt>[1]) =>
      api.renderPrompt(sessionId!, request),
  })
}
