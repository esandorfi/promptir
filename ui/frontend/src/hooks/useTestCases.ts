import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api/client'
import { useWorkbenchStore } from '../stores/workbench'
import type { TestCaseInput, TestCaseResponse } from '../types'

export function useTestCases(promptId: string | undefined, version: string | undefined) {
  const sessionId = useWorkbenchStore((s) => s.sessionId)

  return useQuery({
    queryKey: ['testcases', sessionId, promptId, version],
    queryFn: () => api.getTestCases(sessionId!, promptId!, version!),
    enabled: !!sessionId && !!promptId && !!version,
  })
}

export function useCreateTestCase() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      promptId,
      version,
      name,
      inputs,
    }: {
      promptId: string
      version: string
      name: string
      inputs: TestCaseInput
    }) => api.createTestCase(sessionId!, promptId, version, name, inputs),
    onSuccess: (_, { promptId, version }) => {
      queryClient.invalidateQueries({
        queryKey: ['testcases', sessionId, promptId, version],
      })
    },
  })
}

export function useUpdateTestCase() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      promptId,
      version,
      testcaseId,
      updates,
    }: {
      promptId: string
      version: string
      testcaseId: string
      updates: {
        name?: string
        inputs?: TestCaseInput
        last_response?: TestCaseResponse
      }
    }) => api.updateTestCase(sessionId!, promptId, version, testcaseId, updates),
    onSuccess: (_, { promptId, version }) => {
      queryClient.invalidateQueries({
        queryKey: ['testcases', sessionId, promptId, version],
      })
    },
  })
}

export function useDeleteTestCase() {
  const sessionId = useWorkbenchStore((s) => s.sessionId)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      promptId,
      version,
      testcaseId,
    }: {
      promptId: string
      version: string
      testcaseId: string
    }) => api.deleteTestCase(sessionId!, promptId, version, testcaseId),
    onSuccess: (_, { promptId, version }) => {
      queryClient.invalidateQueries({
        queryKey: ['testcases', sessionId, promptId, version],
      })
    },
  })
}
