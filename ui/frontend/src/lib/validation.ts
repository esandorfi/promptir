export interface ValidationError {
  type: 'undeclared' | 'syntax' | 'naming'
  message: string
  variable?: string
  line?: number
}

export interface ValidationWarning {
  type: 'unused'
  message: string
  variable?: string
}

export interface ValidationResult {
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

const SIMPLE_VAR_PATTERN = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g
const JINJA_VAR_PATTERN = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g
const JINJA_BLOCK_PATTERN = /\{%\s*(?:if|for|elif)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g

const VARIABLE_NAME_PATTERN = /^[a-z][a-z0-9_]*$/
const BLOCK_NAME_PATTERN = /^_[a-z][a-z0-9_]*$/

export function extractUsedVariables(
  content: string,
  templateEngine: string = 'simple'
): Set<string> {
  const used = new Set<string>()

  // Simple pattern - works for both engines
  let match
  while ((match = SIMPLE_VAR_PATTERN.exec(content)) !== null) {
    used.add(match[1])
  }

  // Jinja-specific patterns
  if (templateEngine === 'jinja2_sandbox') {
    JINJA_VAR_PATTERN.lastIndex = 0
    while ((match = JINJA_VAR_PATTERN.exec(content)) !== null) {
      used.add(match[1])
    }
    while ((match = JINJA_BLOCK_PATTERN.exec(content)) !== null) {
      used.add(match[1])
    }
  }

  return used
}

export function validateTemplate(
  body: string,
  declaredVars: string[],
  declaredBlocks: Record<string, unknown>,
  templateEngine: string = 'simple'
): ValidationResult {
  const errors: ValidationError[] = []
  const warnings: ValidationWarning[] = []

  const declared = new Set([...declaredVars, ...Object.keys(declaredBlocks)])
  const used = extractUsedVariables(body, templateEngine)

  // Check for undeclared variables
  for (const v of used) {
    if (!declared.has(v)) {
      errors.push({
        type: 'undeclared',
        message: `Undeclared variable: ${v}`,
        variable: v,
      })
    }
  }

  // Check for unused declared variables
  for (const v of declared) {
    if (!used.has(v)) {
      warnings.push({
        type: 'unused',
        message: `Declared but unused: ${v}`,
        variable: v,
      })
    }
  }

  // Check naming conventions
  for (const v of declaredVars) {
    if (v.startsWith('_')) {
      errors.push({
        type: 'naming',
        message: `Variable '${v}' starts with underscore - should be a block`,
        variable: v,
      })
    } else if (!VARIABLE_NAME_PATTERN.test(v)) {
      errors.push({
        type: 'naming',
        message: `Variable '${v}' doesn't match pattern [a-z][a-z0-9_]*`,
        variable: v,
      })
    }
  }

  for (const b of Object.keys(declaredBlocks)) {
    if (!BLOCK_NAME_PATTERN.test(b)) {
      errors.push({
        type: 'naming',
        message: `Block '${b}' doesn't match pattern _[a-z][a-z0-9_]*`,
        variable: b,
      })
    }
  }

  return { errors, warnings }
}

export function validateFrontmatter(
  frontmatter: Record<string, unknown>
): ValidationResult {
  const errors: ValidationError[] = []
  const warnings: ValidationWarning[] = []

  // Required fields
  if (!frontmatter.id) {
    errors.push({ type: 'syntax', message: 'Missing required field: id' })
  } else if (typeof frontmatter.id !== 'string') {
    errors.push({ type: 'syntax', message: 'Field "id" must be a string' })
  }

  if (!frontmatter.version) {
    errors.push({ type: 'syntax', message: 'Missing required field: version' })
  } else if (typeof frontmatter.version !== 'string') {
    errors.push({ type: 'syntax', message: 'Field "version" must be a string' })
  }

  // Template engine
  if (
    frontmatter.template_engine &&
    !['simple', 'jinja2_sandbox'].includes(frontmatter.template_engine as string)
  ) {
    errors.push({
      type: 'syntax',
      message: 'template_engine must be "simple" or "jinja2_sandbox"',
    })
  }

  // Variables must be an array
  if (frontmatter.variables && !Array.isArray(frontmatter.variables)) {
    errors.push({ type: 'syntax', message: 'Field "variables" must be an array' })
  }

  // Blocks must be an object
  if (frontmatter.blocks && typeof frontmatter.blocks !== 'object') {
    errors.push({ type: 'syntax', message: 'Field "blocks" must be an object' })
  }

  return { errors, warnings }
}
