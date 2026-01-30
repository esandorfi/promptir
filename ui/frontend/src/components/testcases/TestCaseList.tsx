import { useState } from 'react'
import { Plus, Play, Trash2, Save } from 'lucide-react'
import { Button, Input } from '../ui'
import { useTestCases, useCreateTestCase, useDeleteTestCase } from '../../hooks/useTestCases'
import { useWorkbenchStore } from '../../stores/workbench'
import { cn } from '../../lib/utils'
import type { TestCase } from '../../types'

interface TestCaseListProps {
  promptId: string
  version: string
}

export function TestCaseList({ promptId, version }: TestCaseListProps) {
  const { data: testCases, isLoading } = useTestCases(promptId, version)
  const createTestCase = useCreateTestCase()
  const deleteTestCase = useDeleteTestCase()

  const testVars = useWorkbenchStore((s) => s.testVars)
  const testBlocks = useWorkbenchStore((s) => s.testBlocks)
  const setTestVars = useWorkbenchStore((s) => s.setTestVars)
  const setTestBlocks = useWorkbenchStore((s) => s.setTestBlocks)

  const [newName, setNewName] = useState('')

  const handleSaveTestCase = () => {
    if (!newName.trim()) return

    createTestCase.mutate(
      {
        promptId,
        version,
        name: newName.trim(),
        inputs: { vars: testVars, blocks: testBlocks },
      },
      {
        onSuccess: () => setNewName(''),
      }
    )
  }

  const handleLoadTestCase = (tc: TestCase) => {
    setTestVars(tc.inputs.vars)
    setTestBlocks(tc.inputs.blocks)
  }

  const handleDeleteTestCase = (tcId: string) => {
    if (!confirm('Delete this test case?')) return
    deleteTestCase.mutate({ promptId, version, testcaseId: tcId })
  }

  if (isLoading) {
    return <div className="p-4 text-muted-foreground">Loading test cases...</div>
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      {/* Save current as test case */}
      <div className="mb-4 flex items-center gap-2">
        <Input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Test case name..."
          className="flex-1"
        />
        <Button
          onClick={handleSaveTestCase}
          disabled={!newName.trim() || createTestCase.isPending}
        >
          <Save className="mr-1.5 h-3.5 w-3.5" />
          Save Current
        </Button>
      </div>

      {/* Test case list */}
      <div className="space-y-2">
        {(testCases || []).length === 0 && (
          <p className="text-center text-sm text-muted-foreground">
            No test cases saved yet
          </p>
        )}

        {(testCases || []).map((tc) => (
          <div
            key={tc.id}
            className="flex items-center gap-2 rounded border border-border p-2"
          >
            <div className="flex-1">
              <div className="font-medium text-sm">{tc.name}</div>
              <div className="text-xs text-muted-foreground">
                {Object.keys(tc.inputs.vars).length} vars,{' '}
                {Object.keys(tc.inputs.blocks).length} blocks
                {tc.last_response && (
                  <span className="ml-2">
                    • Last run: {new Date(tc.last_response.timestamp).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>

            <Button variant="outline" size="sm" onClick={() => handleLoadTestCase(tc)}>
              <Play className="mr-1 h-3 w-3" />
              Load
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => handleDeleteTestCase(tc.id)}
            >
              <Trash2 className="h-3.5 w-3.5 text-destructive" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}
