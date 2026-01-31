export * from './prompt'
export * from './session'
export * from './testcase'

// Validation types
export interface ValidationError {
  type: string
  message: string
  line?: number
  variable?: string
}

export interface ValidationWarning {
  type: string
  message: string
  variable?: string
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

// Compile types
export interface CompileResult {
  success: boolean
  manifest_path: string | null
  errors: ValidationError[]
  prompts_compiled: number
}

// Render types
export interface RenderRequest {
  prompt_id: string
  version?: string
  vars: Record<string, string>
  blocks: Record<string, string>
}

export interface RenderResponse {
  messages: { role: string; content: string }[]
  token_estimate: number
}

// Inference types
export interface InferenceRequest {
  messages: { role: string; content: string }[]
  model: string
  temperature: number
  max_tokens: number
}

export interface InferenceResponse {
  content: string
  model: string
  input_tokens: number
  output_tokens: number
  latency_ms: number
  cost_estimate: number | null
}

// Diff types
export interface DiffResponse {
  prompt_id: string
  version1: string
  version2: string
  frontmatter_diff: string
  template_diff: string
}
