import { describe, it, expect } from 'vitest'
import {
  extractUsedVariables,
  validateTemplate,
  validateFrontmatter,
} from '../lib/validation'

describe('extractUsedVariables', () => {
  it('should extract simple template variables', () => {
    const content = 'Hello {{name}}, your id is {{user_id}}'
    const used = extractUsedVariables(content)

    expect(used).toContain('name')
    expect(used).toContain('user_id')
    expect(used.size).toBe(2)
  })

  it('should handle whitespace in template tags', () => {
    const content = '{{ name }} and {{  spaced  }}'
    const used = extractUsedVariables(content)

    expect(used).toContain('name')
    expect(used).toContain('spaced')
  })

  it('should extract jinja block variables', () => {
    const content = '{% if show_context %}{{context}}{% endif %}'
    const used = extractUsedVariables(content, 'jinja2_sandbox')

    expect(used).toContain('show_context')
    expect(used).toContain('context')
  })

  it('should handle empty content', () => {
    const used = extractUsedVariables('')
    expect(used.size).toBe(0)
  })

  it('should ignore non-variable patterns', () => {
    const content = '{ not a var } and {also not}'
    const used = extractUsedVariables(content)
    expect(used.size).toBe(0)
  })
})

describe('validateTemplate', () => {
  it('should detect undeclared variables', () => {
    const body = 'Hello {{name}} and {{unknown}}'
    const result = validateTemplate(body, ['name'], {})

    expect(result.errors).toHaveLength(1)
    expect(result.errors[0].type).toBe('undeclared')
    expect(result.errors[0].variable).toBe('unknown')
  })

  it('should detect unused declared variables', () => {
    const body = 'Hello {{name}}'
    const result = validateTemplate(body, ['name', 'unused'], {})

    expect(result.warnings).toHaveLength(1)
    expect(result.warnings[0].type).toBe('unused')
    expect(result.warnings[0].variable).toBe('unused')
  })

  it('should allow blocks to be used', () => {
    const body = 'Context: {{_rag_context}}'
    const result = validateTemplate(body, [], { _rag_context: {} })

    expect(result.errors).toHaveLength(0)
  })

  it('should flag variables starting with underscore', () => {
    const body = '{{_bad_var}}'
    const result = validateTemplate(body, ['_bad_var'], {})

    expect(result.errors.some(e => e.type === 'naming')).toBe(true)
  })

  it('should flag blocks not starting with underscore', () => {
    const body = '{{bad_block}}'
    const result = validateTemplate(body, [], { bad_block: {} })

    expect(result.errors.some(e => e.type === 'naming')).toBe(true)
  })

  it('should accept valid naming conventions', () => {
    const body = '{{question}} {{_context}}'
    const result = validateTemplate(body, ['question'], { _context: {} })

    expect(result.errors.filter(e => e.type === 'naming')).toHaveLength(0)
  })

  it('should validate all declared are used with no extra', () => {
    const body = '{{a}} {{b}} {{_c}}'
    const result = validateTemplate(body, ['a', 'b'], { _c: {} })

    expect(result.errors).toHaveLength(0)
    expect(result.warnings).toHaveLength(0)
  })
})

describe('validateFrontmatter', () => {
  it('should require id field', () => {
    const fm = { version: 'v1' }
    const result = validateFrontmatter(fm)

    expect(result.errors.some(e => e.message.includes('id'))).toBe(true)
  })

  it('should require version field', () => {
    const fm = { id: 'test' }
    const result = validateFrontmatter(fm)

    expect(result.errors.some(e => e.message.includes('version'))).toBe(true)
  })

  it('should validate template_engine values', () => {
    const fm = { id: 'test', version: 'v1', template_engine: 'invalid' }
    const result = validateFrontmatter(fm)

    expect(result.errors.some(e => e.message.includes('template_engine'))).toBe(true)
  })

  it('should accept valid template_engine', () => {
    const fm1 = { id: 'test', version: 'v1', template_engine: 'simple' }
    const fm2 = { id: 'test', version: 'v1', template_engine: 'jinja2_sandbox' }

    expect(validateFrontmatter(fm1).errors.filter(e => e.message.includes('template_engine'))).toHaveLength(0)
    expect(validateFrontmatter(fm2).errors.filter(e => e.message.includes('template_engine'))).toHaveLength(0)
  })

  it('should validate variables is array', () => {
    const fm = { id: 'test', version: 'v1', variables: 'not an array' }
    const result = validateFrontmatter(fm)

    expect(result.errors.some(e => e.message.includes('variables'))).toBe(true)
  })

  it('should validate blocks is object', () => {
    const fm = { id: 'test', version: 'v1', blocks: 'not an object' }
    const result = validateFrontmatter(fm)

    expect(result.errors.some(e => e.message.includes('blocks'))).toBe(true)
  })

  it('should pass valid frontmatter', () => {
    const fm = {
      id: 'test_prompt',
      version: 'v1',
      template_engine: 'simple',
      variables: ['question'],
      blocks: { _context: { optional: true, default: '' } },
    }
    const result = validateFrontmatter(fm)

    expect(result.errors).toHaveLength(0)
  })
})
