import type { CompletionContext, CompletionResult } from '@codemirror/autocomplete'

export function createVariableCompletion(
  variables: string[],
  blocks: string[]
) {
  return function (context: CompletionContext): CompletionResult | null {
    // Match {{ followed by optional variable start
    const before = context.matchBefore(/\{\{\s*[a-zA-Z_]*/)
    if (!before) return null

    // Find where the variable name starts (after {{ and whitespace)
    const match = before.text.match(/\{\{\s*/)
    if (!match) return null

    const varStart = before.from + match[0].length

    return {
      from: varStart,
      options: variables.map((v) => ({
        label: v,
        type: blocks.includes(v) ? 'property' : 'variable',
        detail: blocks.includes(v) ? 'block (enrichment)' : 'variable (required)',
        boost: blocks.includes(v) ? 0 : 1, // Variables first
      })),
    }
  }
}
