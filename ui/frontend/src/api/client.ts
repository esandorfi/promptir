import type {
  Session,
  SessionListResponse,
  PromptListResponse,
  PromptDetail,
  PromptSource,
  CompileResult,
  ValidationResult,
  RenderRequest,
  RenderResponse,
  InferenceRequest,
  InferenceResponse,
  TestCaseListResponse,
  TestCase,
  TestCaseInput,
  TestCaseResponse,
  DiffResponse,
} from '../types'

const BASE_URL = '/api'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Sessions
export async function getSessions(): Promise<Session[]> {
  const data = await fetchJson<SessionListResponse>('/sessions')
  return data.sessions
}

export async function getSession(sessionId: string): Promise<Session> {
  return fetchJson<Session>(`/sessions/${sessionId}`)
}

// Prompts
export async function getPrompts(sessionId: string): Promise<PromptListResponse> {
  return fetchJson<PromptListResponse>(`/sessions/${sessionId}/prompts`)
}

export async function getPrompt(
  sessionId: string,
  promptId: string,
  version?: string
): Promise<PromptDetail> {
  const url = version
    ? `/sessions/${sessionId}/prompts/${promptId}/${version}`
    : `/sessions/${sessionId}/prompts/${promptId}`
  return fetchJson<PromptDetail>(url)
}

export async function getPromptSource(
  sessionId: string,
  promptId: string,
  version: string
): Promise<PromptSource> {
  return fetchJson<PromptSource>(`/sessions/${sessionId}/prompts/${promptId}/${version}/source`)
}

export async function updatePrompt(
  sessionId: string,
  promptId: string,
  version: string,
  content: string
): Promise<PromptSource> {
  return fetchJson<PromptSource>(`/sessions/${sessionId}/prompts/${promptId}/${version}`, {
    method: 'PUT',
    body: JSON.stringify({ content }),
  })
}

export async function createPrompt(
  sessionId: string,
  id: string,
  version: string,
  content: string
): Promise<PromptSource> {
  return fetchJson<PromptSource>(`/sessions/${sessionId}/prompts`, {
    method: 'POST',
    body: JSON.stringify({ id, version, content }),
  })
}

export async function deletePrompt(
  sessionId: string,
  promptId: string,
  version: string
): Promise<{ deleted: boolean }> {
  return fetchJson<{ deleted: boolean }>(
    `/sessions/${sessionId}/prompts/${promptId}/${version}`,
    { method: 'DELETE' }
  )
}

// Compilation
export async function compileSession(sessionId: string): Promise<CompileResult> {
  return fetchJson<CompileResult>(`/sessions/${sessionId}/compile`, {
    method: 'POST',
  })
}

export async function validateSession(sessionId: string): Promise<ValidationResult> {
  return fetchJson<ValidationResult>(`/sessions/${sessionId}/validate`, {
    method: 'POST',
  })
}

export async function renderPrompt(
  sessionId: string,
  request: RenderRequest
): Promise<RenderResponse> {
  return fetchJson<RenderResponse>(`/sessions/${sessionId}/render`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

// Inference
export async function getModels(): Promise<string[]> {
  const data = await fetchJson<{ models: string[] }>('/infer/models')
  return data.models
}

export async function runInference(request: InferenceRequest): Promise<InferenceResponse> {
  return fetchJson<InferenceResponse>('/infer', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

// Test Cases
export async function getTestCases(
  sessionId: string,
  promptId: string,
  version: string
): Promise<TestCase[]> {
  const data = await fetchJson<TestCaseListResponse>(
    `/sessions/${sessionId}/prompts/${promptId}/${version}/testcases`
  )
  return data.test_cases
}

export async function createTestCase(
  sessionId: string,
  promptId: string,
  version: string,
  name: string,
  inputs: TestCaseInput
): Promise<TestCase> {
  return fetchJson<TestCase>(
    `/sessions/${sessionId}/prompts/${promptId}/${version}/testcases`,
    {
      method: 'POST',
      body: JSON.stringify({ name, inputs }),
    }
  )
}

export async function updateTestCase(
  sessionId: string,
  promptId: string,
  version: string,
  testcaseId: string,
  updates: {
    name?: string
    inputs?: TestCaseInput
    last_response?: TestCaseResponse
  }
): Promise<TestCase> {
  return fetchJson<TestCase>(
    `/sessions/${sessionId}/prompts/${promptId}/${version}/testcases/${testcaseId}`,
    {
      method: 'PUT',
      body: JSON.stringify(updates),
    }
  )
}

export async function deleteTestCase(
  sessionId: string,
  promptId: string,
  version: string,
  testcaseId: string
): Promise<{ deleted: boolean }> {
  return fetchJson<{ deleted: boolean }>(
    `/sessions/${sessionId}/prompts/${promptId}/${version}/testcases/${testcaseId}`,
    { method: 'DELETE' }
  )
}

// Diff
export async function getDiff(
  sessionId: string,
  promptId: string,
  v1: string,
  v2: string
): Promise<DiffResponse> {
  return fetchJson<DiffResponse>(
    `/sessions/${sessionId}/prompts/${promptId}/diff?v1=${v1}&v2=${v2}`
  )
}
