import { createContext, useContext, useMemo, useEffect } from 'react'
import type { ReactNode } from 'react'
import { usePortfolioSummary } from '../../hooks/usePortfolio'
import { useAppStore } from '../../store/useAppStore'

interface PortfolioContextValue {
  summary: Record<string, unknown> | undefined
  loading: boolean
  allRows: Record<string, unknown>[]
  selectedAssetRow: Record<string, unknown> | undefined
  availableTags: string[]
}

const Ctx = createContext<PortfolioContextValue | undefined>(undefined)

const EMPTY_TAGS: string[] = []

export function PortfolioProvider({ children }: { children: ReactNode }) {
  const { selectedTickers, setSelectedTickers, selectedTags } = useAppStore()
  const { data: summary, isLoading } = usePortfolioSummary()

  const availableTags = (summary?.available_tags as string[]) ?? EMPTY_TAGS

  const allRows = useMemo(() => {
    const rows = (summary?.asset_table?.rows as Record<string, unknown>[]) ?? []
    if (!selectedTags.length) return rows
    return rows.filter((r) => {
      const tags = (r.tags as string[]) ?? []
      return selectedTags.some((t) => tags.includes(t))
    })
  }, [summary?.asset_table?.rows, selectedTags])

  useEffect(() => {
    if (selectedTickers.length === 0 && allRows.length > 0) {
      setSelectedTickers([allRows[0].ticker as string])
    }
  }, [allRows]) // eslint-disable-line react-hooks/exhaustive-deps

  const selectedAssetRow = useMemo(() => {
    if (!selectedTickers.length) return undefined
    return allRows.find((r) => r.ticker === selectedTickers[0])
  }, [selectedTickers, allRows])

  const value = useMemo<PortfolioContextValue>(() => ({
    summary: summary as Record<string, unknown> | undefined,
    loading: isLoading,
    allRows,
    selectedAssetRow,
    availableTags,
  }), [summary, isLoading, allRows, selectedAssetRow, availableTags])

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function usePortfolioContext() {
  const v = useContext(Ctx)
  if (!v) throw new Error('usePortfolioContext must be used inside PortfolioProvider')
  return v
}
