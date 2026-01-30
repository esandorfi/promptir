import { useEffect } from 'react'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface DarkModeState {
  isDark: boolean
  toggle: () => void
  setDark: (dark: boolean) => void
}

export const useDarkModeStore = create<DarkModeState>()(
  persist(
    (set) => ({
      isDark: false,
      toggle: () => set((state) => ({ isDark: !state.isDark })),
      setDark: (dark) => set({ isDark: dark }),
    }),
    {
      name: 'promptir-dark-mode',
    }
  )
)

export function useDarkMode() {
  const { isDark, toggle, setDark } = useDarkModeStore()

  // Apply dark class to document
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  // Initialize from system preference
  useEffect(() => {
    const stored = localStorage.getItem('promptir-dark-mode')
    if (!stored) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setDark(prefersDark)
    }
  }, [setDark])

  return { isDark, toggle }
}
