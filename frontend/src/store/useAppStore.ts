import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { PaletteMode } from '@mui/material'

type TimeframeOption = '7d' | '30d' | '90d' | '180d' | '365d' | 'all'

interface AppState {
  // Theme
  themeMode: PaletteMode
  toggleTheme: () => void

  // Privacy
  privacyMode: boolean
  togglePrivacy: () => void

  // Selected tickers in the asset table
  selectedTickers: string[]
  setSelectedTickers: (tickers: string[]) => void

  // Timeframe filter
  timeframe: TimeframeOption
  setTimeframe: (tf: TimeframeOption) => void

  // Custom date range (ISO strings)
  fromDate: string | null
  toDate: string | null
  setDateRange: (from: string | null, to: string | null) => void

  // Active tag filters
  selectedTags: string[]
  setSelectedTags: (tags: string[]) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      themeMode: 'dark',
      toggleTheme: () =>
        set((s) => ({ themeMode: s.themeMode === 'dark' ? 'light' : 'dark' })),

      privacyMode: false,
      togglePrivacy: () => set((s) => ({ privacyMode: !s.privacyMode })),

      selectedTickers: [],
      setSelectedTickers: (tickers) => set({ selectedTickers: tickers }),

      timeframe: '30d',
      setTimeframe: (tf) => set({ timeframe: tf }),

      fromDate: null,
      toDate: null,
      setDateRange: (from, to) => set({ fromDate: from, toDate: to }),

      selectedTags: [],
      setSelectedTags: (tags) => set({ selectedTags: tags }),
    }),
    {
      name: 'portfolio-app-store',
      partialize: (state) => ({
        themeMode: state.themeMode,
        privacyMode: state.privacyMode,
        timeframe: state.timeframe,
      }),
    },
  ),
)
