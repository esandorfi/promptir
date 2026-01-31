export interface TestCaseInput {
  vars: Record<string, string>
  blocks: Record<string, string>
}

export interface TestCaseResponse {
  content: string
  model: string
  tokens_in: number
  tokens_out: number
  latency_ms: number
  timestamp: string
}

export interface TestCase {
  id: string
  name: string
  created_at: string
  inputs: TestCaseInput
  last_response: TestCaseResponse | null
}

export interface TestCaseListResponse {
  prompt_id: string
  version: string
  test_cases: TestCase[]
}
