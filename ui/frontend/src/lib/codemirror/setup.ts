import { EditorView, keymap, lineNumbers, highlightActiveLineGutter, highlightActiveLine } from '@codemirror/view'
import { EditorState, Extension } from '@codemirror/state'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { bracketMatching } from '@codemirror/language'
import { autocompletion, closeBrackets, closeBracketsKeymap } from '@codemirror/autocomplete'
import { highlightSelectionMatches, searchKeymap } from '@codemirror/search'
import { jinjaHighlight, jinjaLanguageSupport } from './jinja-highlight'
import { createVariableCompletion } from './autocomplete'

export interface EditorConfig {
  variables?: string[]
  blocks?: string[]
  onChange?: (value: string) => void
  readOnly?: boolean
}

export function createEditorExtensions(config: EditorConfig = {}): Extension[] {
  const extensions: Extension[] = [
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightActiveLine(),
    history(),
    bracketMatching(),
    closeBrackets(),
    highlightSelectionMatches(),
    keymap.of([
      ...closeBracketsKeymap,
      ...defaultKeymap,
      ...searchKeymap,
      ...historyKeymap,
    ]),
    jinjaHighlight,
    jinjaLanguageSupport(),
    EditorView.lineWrapping,
    EditorView.theme({
      '&': {
        fontSize: '13px',
      },
      '.cm-content': {
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      },
      '.cm-gutters': {
        backgroundColor: 'transparent',
        borderRight: '1px solid hsl(var(--border))',
      },
      '.cm-activeLineGutter': {
        backgroundColor: 'hsl(var(--muted))',
      },
    }),
  ]

  // Add variable autocompletion
  const allVars = [...(config.variables || []), ...(config.blocks || [])]
  if (allVars.length > 0) {
    extensions.push(
      autocompletion({
        override: [createVariableCompletion(allVars, config.blocks || [])],
      })
    )
  }

  // Handle changes
  if (config.onChange) {
    extensions.push(
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          config.onChange!(update.state.doc.toString())
        }
      })
    )
  }

  // Read-only mode
  if (config.readOnly) {
    extensions.push(EditorState.readOnly.of(true))
  }

  return extensions
}
