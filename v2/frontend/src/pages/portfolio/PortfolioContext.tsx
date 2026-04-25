import { createContext, useContext, useMemo, useEffect } from 'react'
import type { ReactNode } from 'react'
import { usePortfolioSummary } from './hooks/usePortfolio'
import { useAppStore } from '../../store/useAppStore'
import { filterAssetsByTags } from '../../presenters/portfolioPresenter'
import type { PortfolioSummaryVM, RawAsset } from '../../presenters/portfolioPresenter'

interface PortfolioContextValue {
  summary: PortfolioSummaryVM | undefined
  loading: boolean
  allRows: RawAsset[]
  selectedAssetRow: RawAsset | undefined
  availableTags: string[]
}

const Ctx = createContext<PortfolioContextValue | undefined>(undefined)

const EMPTY_TAGS: string[] = []

export function PortfolioProvider({ children }: { children: ReactNode }) {
  const { selectedTickers, setSelectedTickers, selectedTags } = useAppStore()
  const { data: summary, isLoading } = usePortfolioSummary()

  const availableTags = summary?.available_tags ?? EMPTY_TAGS

  const allRows = useMemo(
    () => filterAssetsByTags(summary?.asset_table?.rows ?? [], selectedTags),
    [summary?.asset_table?.rows, selectedTags],
  )

  useEffect(() => {
    if (selectedTickers.length === 0 && allRows.length > 0) {
      setSelectedTickers([allRows[0].ticker])
    }
  }, [allRows]) // eslint-disable-line react-hooks/exhaustive-deps

  const selectedAssetRow = useMemo(() => {
    if (!selectedTickers.length) return undefined
    return allRows.find((r) => r.ticker === selectedTickers[0])
  }, [selectedTickers, allRows])

  const value = useMemo<PortfolioContextValue>(() => ({
    summary,
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
