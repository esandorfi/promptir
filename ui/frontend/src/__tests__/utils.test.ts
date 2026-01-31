import { describe, it, expect } from 'vitest'
import {
  parsePromptContent,
  serializePromptContent,
  parseSections,
  serializeSections,
  formatCost,
  formatLatency,
  formatTokens,
} from '../lib/utils'

describe('parsePromptContent', () => {
  it('should parse valid frontmatter and body', () => {
    const content = `---
{
  "id": "test",
  "version": "v1"
}
---
# system
Hello`

    const { frontmatter, body } = parsePromptContent(content)

    expect(frontmatter).not.toBeNull()
    expect(frontmatter?.id).toBe('test')
    expect(frontmatter?.version).toBe('v1')
    expect(body).toContain('# system')
  })

  it('should handle content without frontmatter', () => {
    const content = '# system\nHello'
    const { frontmatter, body } = parsePromptContent(content)

    expect(frontmatter).toBeNull()
    expect(body).toBe(content)
  })

  it('should handle invalid JSON frontmatter', () => {
    const content = `---
{invalid json}
---
# system`

    const { frontmatter, body } = parsePromptContent(content)
    expect(frontmatter).toBeNull()
  })

  it('should handle unclosed frontmatter', () => {
    const content = `---
{"id": "test"}
# system`

    const { frontmatter, body } = parsePromptContent(content)
    expect(frontmatter).toBeNull()
  })
})

describe('serializePromptContent', () => {
  it('should serialize frontmatter and body', () => {
    const frontmatter = { id: 'test', version: 'v1' }
    const body = '# system\nHello'

    const result = serializePromptContent(frontmatter, body)

    expect(result).toContain('---')
    expect(result).toContain('"id": "test"')
    expect(result).toContain('# system')
  })

  it('should be reversible with parsePromptContent', () => {
    const original = { id: 'test', version: 'v1', variables: ['a', 'b'] }
    const body = '# system\nHello\n\n# user\nWorld'

    const serialized = serializePromptContent(original, body)
    const { frontmatter, body: parsedBody } = parsePromptContent(serialized)

    expect(frontmatter?.id).toBe(original.id)
    expect(frontmatter?.variables).toEqual(original.variables)
    expect(parsedBody.trim()).toBe(body)
  })
})

describe('parseSections', () => {
  it('should parse role sections', () => {
    const body = `# system
System content here

# user
User content here

# assistant
Assistant content`

    const sections = parseSections(body)

    expect(sections).toHaveLength(3)
    expect(sections[0].role).toBe('system')
    expect(sections[0].content).toBe('System content here')
    expect(sections[1].role).toBe('user')
    expect(sections[2].role).toBe('assistant')
  })

  it('should handle single section', () => {
    const body = '# system\nOnly system'
    const sections = parseSections(body)

    expect(sections).toHaveLength(1)
    expect(sections[0].role).toBe('system')
  })

  it('should handle empty body', () => {
    const sections = parseSections('')
    expect(sections).toHaveLength(0)
  })

  it('should ignore content before first role', () => {
    const body = `Some preamble
# system
Content`

    const sections = parseSections(body)
    expect(sections).toHaveLength(1)
    expect(sections[0].content).toBe('Content')
  })
})

describe('serializeSections', () => {
  it('should serialize sections back to body', () => {
    const sections = [
      { role: 'system', content: 'System content' },
      { role: 'user', content: 'User content' },
    ]

    const result = serializeSections(sections)

    expect(result).toContain('# system')
    expect(result).toContain('# user')
    expect(result).toContain('System content')
  })
})

describe('formatCost', () => {
  it('should format null as dash', () => {
    expect(formatCost(null)).toBe('-')
    expect(formatCost(undefined)).toBe('-')
  })

  it('should format small costs with 4 decimals', () => {
    expect(formatCost(0.001)).toBe('$0.0010')
    expect(formatCost(0.0005)).toBe('$0.0005')
  })

  it('should format larger costs with 3 decimals', () => {
    expect(formatCost(0.05)).toBe('$0.050')
    expect(formatCost(1.234)).toBe('$1.234')
  })
})

describe('formatLatency', () => {
  it('should format milliseconds', () => {
    expect(formatLatency(500)).toBe('500ms')
    expect(formatLatency(999)).toBe('999ms')
  })

  it('should format seconds', () => {
    expect(formatLatency(1000)).toBe('1.0s')
    expect(formatLatency(1500)).toBe('1.5s')
    expect(formatLatency(2345)).toBe('2.3s')
  })
})

describe('formatTokens', () => {
  it('should format small numbers as-is', () => {
    expect(formatTokens(100)).toBe('100')
    expect(formatTokens(999)).toBe('999')
  })

  it('should format thousands with k suffix', () => {
    expect(formatTokens(1000)).toBe('1.0k')
    expect(formatTokens(1500)).toBe('1.5k')
    expect(formatTokens(12345)).toBe('12.3k')
  })
})
