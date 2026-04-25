import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { PaletteMode } from '@mui/material'
import { TIMEFRAME_OPTIONS, type TimeframeOption } from '../constants/timeframes'

export type { TimeframeOption }

export type Density = 'compact' | 'comfortable'

const VALID_TIMEFRAMES: Set<string> = new Set(TIMEFRAME_OPTIONS.map((o) => o.value))

interface AppState {
  // Theme
  themeMode: PaletteMode
  toggleTheme: () => void

  // Privacy
  privacyMode: boolean
  togglePrivacy: () => void

  // Density
  density: Density
  setDensity: (d: Density) => void
  toggleDensity: () => void

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

      density: 'compact',
      setDensity: (d) => set({ density: d }),
      toggleDensity: () =>
        set((s) => ({ density: s.density === 'compact' ? 'comfortable' : 'compact' })),

      selectedTickers: [],
      setSelectedTickers: (tickers) => set({ selectedTickers: tickers }),

      timeframe: '6m',
      setTimeframe: (tf) => set({ timeframe: tf }),

      fromDate: null,
      toDate: null,
      setDateRange: (from, to) => set({ fromDate: from, toDate: to }),

      selectedTags: [],
      setSelectedTags: (tags) => set({ selectedTags: tags }),
    }),
    {
      name: 'portfolio-app-store',
      version: 1,
      migrate: (persisted: unknown) => {
        const s = persisted as Record<string, unknown>
        return {
          ...s,
          timeframe: VALID_TIMEFRAMES.has(s.timeframe as string) ? s.timeframe : '6m',
        }
      },
      partialize: (state) => ({
        themeMode: state.themeMode,
        privacyMode: state.privacyMode,
        timeframe: state.timeframe,
        density: state.density,
      }),
    },
  ),
)
