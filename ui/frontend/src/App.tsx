import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { PromptEditor } from './components/prompts/PromptEditor'
import { PreviewPanel } from './components/preview/PreviewPanel'
import { usePromptDetail } from './hooks/usePrompts'
import { useWorkbenchStore } from './stores/workbench'

export default function App() {
  const selectedPrompt = useWorkbenchStore((s) => s.selectedPrompt)
  const { data: promptDetail } = usePromptDetail(
    selectedPrompt?.id,
    selectedPrompt?.version
  )

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />

        <main className="flex flex-1 flex-col overflow-hidden">
          <PromptEditor />
          <PreviewPanel prompt={promptDetail} />
        </main>
      </div>
    </div>
  )
}
