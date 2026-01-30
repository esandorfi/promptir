import { useQuery, useMutation } from '@tanstack/react-query'
import * as api from '../api/client'
import type { InferenceRequest } from '../types'

export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: api.getModels,
    staleTime: 1000 * 60 * 60, // 1 hour
  })
}

export function useInference() {
  return useMutation({
    mutationFn: (request: InferenceRequest) => api.runInference(request),
  })
}
