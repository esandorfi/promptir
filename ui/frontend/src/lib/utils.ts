import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function parsePromptContent(content: string): {
  frontmatter: Record<string, unknown> | null
  body: string
} {
  const lines = content.split('\n')

  if (!lines.length || lines[0].trim() !== '---') {
    return { frontmatter: null, body: content }
  }

  let endIdx: number | null = null
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      endIdx = i
      break
    }
  }

  if (endIdx === null) {
    return { frontmatter: null, body: content }
  }

  const frontmatterStr = lines.slice(1, endIdx).join('\n')
  const body = lines.slice(endIdx + 1).join('\n')

  try {
    const frontmatter = JSON.parse(frontmatterStr)
    return { frontmatter, body }
  } catch {
    return { frontmatter: null, body: content }
  }
}

export function serializePromptContent(
  frontmatter: Record<string, unknown>,
  body: string
): string {
  const frontmatterStr = JSON.stringify(frontmatter, null, 2)
  return `---\n${frontmatterStr}\n---\n${body}`
}

export function parseSections(body: string): { role: string; content: string }[] {
  const sections: { role: string; content: string }[] = []
  const lines = body.split('\n')

  let currentRole: string | null = null
  let currentContent: string[] = []

  for (const line of lines) {
    const roleMatch = line.match(/^#\s+(system|user|assistant)\s*$/)
    if (roleMatch) {
      if (currentRole) {
        sections.push({
          role: currentRole,
          content: currentContent.join('\n').trim(),
        })
      }
      currentRole = roleMatch[1]
      currentContent = []
    } else if (currentRole) {
      currentContent.push(line)
    }
  }

  if (currentRole) {
    sections.push({
      role: currentRole,
      content: currentContent.join('\n').trim(),
    })
  }

  return sections
}

export function serializeSections(sections: { role: string; content: string }[]): string {
  return sections.map((s) => `# ${s.role}\n${s.content}`).join('\n\n')
}

export function formatCost(cost: number | null | undefined): string {
  if (cost === null || cost === undefined) return '-'
  if (cost < 0.01) return `$${cost.toFixed(4)}`
  return `$${cost.toFixed(3)}`
}

export function formatLatency(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export function formatTokens(tokens: number): string {
  if (tokens < 1000) return tokens.toString()
  return `${(tokens / 1000).toFixed(1)}k`
}
