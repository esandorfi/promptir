import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SelectedPrompt {
  id: string
  version: string
}

interface WorkbenchState {
  // Session
  sessionId: string | null
  setSessionId: (id: string) => void

  // Selected prompt
  selectedPrompt: SelectedPrompt | null
  setSelectedPrompt: (prompt: SelectedPrompt | null) => void

  // Editor state
  isDirty: boolean
  setIsDirty: (dirty: boolean) => void
  draftContent: string | null
  setDraftContent: (content: string | null) => void

  // UI state
  previewExpanded: boolean
  setPreviewExpanded: (expanded: boolean) => void
  activeTab: 'metadata' | 'inputs' | 'template' | 'testcases'
  setActiveTab: (tab: 'metadata' | 'inputs' | 'template' | 'testcases') => void

  // Test inputs
  testVars: Record<string, string>
  setTestVars: (vars: Record<string, string>) => void
  testBlocks: Record<string, string>
  setTestBlocks: (blocks: Record<string, string>) => void

  // Inference settings
  inferenceModel: string
  setInferenceModel: (model: string) => void
  inferenceTemp: number
  setInferenceTemp: (temp: number) => void
  inferenceMaxTokens: number
  setInferenceMaxTokens: (tokens: number) => void
}

export const useWorkbenchStore = create<WorkbenchState>()(
  persist(
    (set) => ({
      // Session - persisted
      sessionId: null,
      setSessionId: (id) => set({ sessionId: id, selectedPrompt: null }),

      // Selected prompt
      selectedPrompt: null,
      setSelectedPrompt: (prompt) =>
        set({
          selectedPrompt: prompt,
          isDirty: false,
          draftContent: null,
          testVars: {},
          testBlocks: {},
        }),

      // Editor state
      isDirty: false,
      setIsDirty: (dirty) => set({ isDirty: dirty }),
      draftContent: null,
      setDraftContent: (content) => set({ draftContent: content, isDirty: content !== null }),

      // UI state
      previewExpanded: true,
      setPreviewExpanded: (expanded) => set({ previewExpanded: expanded }),
      activeTab: 'template',
      setActiveTab: (tab) => set({ activeTab: tab }),

      // Test inputs
      testVars: {},
      setTestVars: (vars) => set({ testVars: vars }),
      testBlocks: {},
      setTestBlocks: (blocks) => set({ testBlocks: blocks }),

      // Inference settings - persisted
      inferenceModel: 'gpt-4o-mini',
      setInferenceModel: (model) => set({ inferenceModel: model }),
      inferenceTemp: 0.7,
      setInferenceTemp: (temp) => set({ inferenceTemp: temp }),
      inferenceMaxTokens: 1024,
      setInferenceMaxTokens: (tokens) => set({ inferenceMaxTokens: tokens }),
    }),
    {
      name: 'promptir-workbench',
      partialize: (state) => ({
        sessionId: state.sessionId,
        inferenceModel: state.inferenceModel,
        inferenceTemp: state.inferenceTemp,
        inferenceMaxTokens: state.inferenceMaxTokens,
        previewExpanded: state.previewExpanded,
      }),
    }
  )
)
