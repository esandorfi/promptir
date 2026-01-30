import { HighlightStyle, syntaxHighlighting, StreamLanguage } from '@codemirror/language'
import { tags } from '@lezer/highlight'

// Custom Jinja syntax highlighting colors
export const jinjaHighlight = syntaxHighlighting(
  HighlightStyle.define([
    // Jinja delimiters {{ }} {% %}
    { tag: tags.processingInstruction, color: '#22c55e', fontWeight: '500' },
    // Variable names inside Jinja
    { tag: tags.variableName, color: '#3b82f6' },
    // Jinja keywords (if, for, endif, etc.)
    { tag: tags.keyword, color: '#a855f7', fontWeight: '500' },
    // Role headers (# system, # user, # assistant)
    { tag: tags.heading, color: '#f59e0b', fontWeight: '600' },
    // Comments
    { tag: tags.comment, color: '#6b7280', fontStyle: 'italic' },
    // Strings
    { tag: tags.string, color: '#10b981' },
  ])
)

// Simple stream-based parser for Jinja + Markdown prompt format
const jinjaStreamParser = {
  startState() {
    return {
      inJinjaExpr: false,
      inJinjaBlock: false,
    }
  },
  token(stream: { match: (pattern: RegExp) => boolean | string[] | null; next: () => string; skipToEnd: () => void; eol: () => boolean; sol: () => boolean }, state: { inJinjaExpr: boolean; inJinjaBlock: boolean }) {
    // Role headers at start of line
    if (stream.sol() && stream.match(/^#\s+(system|user|assistant)\s*$/)) {
      return 'heading'
    }

    // Jinja expression start
    if (stream.match('{{')) {
      state.inJinjaExpr = true
      return 'processingInstruction'
    }

    // Jinja expression end
    if (state.inJinjaExpr && stream.match('}}')) {
      state.inJinjaExpr = false
      return 'processingInstruction'
    }

    // Inside Jinja expression - variable names
    if (state.inJinjaExpr) {
      if (stream.match(/[a-zA-Z_][a-zA-Z0-9_]*/)) {
        return 'variableName'
      }
      stream.next()
      return null
    }

    // Jinja block start
    if (stream.match('{%')) {
      state.inJinjaBlock = true
      return 'processingInstruction'
    }

    // Jinja block end
    if (state.inJinjaBlock && stream.match('%}')) {
      state.inJinjaBlock = false
      return 'processingInstruction'
    }

    // Inside Jinja block
    if (state.inJinjaBlock) {
      // Keywords
      if (stream.match(/\b(if|else|elif|endif|for|endfor|block|endblock|extends|include|macro|endmacro|set)\b/)) {
        return 'keyword'
      }
      // Variable names
      if (stream.match(/[a-zA-Z_][a-zA-Z0-9_]*/)) {
        return 'variableName'
      }
      stream.next()
      return null
    }

    // Jinja comment
    if (stream.match('{#')) {
      while (!stream.eol()) {
        if (stream.match('#}')) break
        stream.next()
      }
      return 'comment'
    }

    // Default - advance one character
    stream.next()
    return null
  },
}

export function jinjaLanguageSupport() {
  return StreamLanguage.define(jinjaStreamParser)
}
