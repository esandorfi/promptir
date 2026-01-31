export interface BlockSpec {
  optional: boolean
  default: string
}

export interface PromptMessage {
  role: string
  content: string
}

export interface PromptSummary {
  id: string
  version: string
  template_engine: string
  metadata: Record<string, unknown>
  variables: string[]
  blocks: Record<string, BlockSpec>
}

export interface PromptDetail extends PromptSummary {
  messages: PromptMessage[]
  hash: string
}

export interface PromptSource {
  id: string
  version: string
  content: string
  path: string
}

export interface PromptListResponse {
  prompts: PromptSummary[]
  includes: PromptSummary[]
}

// Parsed prompt for editing
export interface ParsedPrompt {
  frontmatter: PromptFrontmatter | null
  body: string
  sections: PromptSection[]
}

export interface PromptFrontmatter {
  id: string
  version: string
  metadata?: Record<string, unknown>
  variables?: string[]
  blocks?: Record<string, BlockSpec>
  includes?: string[]
  template_engine?: string
}

export interface PromptSection {
  role: string
  content: string
}
