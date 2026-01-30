export interface Session {
  id: string
  name: string
  manifest_path: string
  prompts_dir: string
}

export interface SessionListResponse {
  sessions: Session[]
}
