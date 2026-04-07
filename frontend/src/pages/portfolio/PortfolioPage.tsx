import { useState, useMemo } from 'react'
import { Box, LinearProgress } from '@mui/material'
import { usePortfolioSummary } from '../../hooks/usePortfolio'
import { useAppStore } from '../../store/useAppStore'
import Navbar from '../../components/organisms/Navbar'
import KpiRow from '../../components/molecules/KpiRow'
import FilterBar from '../../components/molecules/FilterBar'
import StatusBar from '../../components/molecules/StatusBar'
import AssetTable from '../../components/organisms/AssetTable'
import WorkspaceSplit from '../../components/organisms/WorkspaceSplit'
import WorkspaceTabs from '../../components/organisms/WorkspaceTabs'
import SettingsModal from '../../components/organisms/SettingsModal'
import RebalanceDrawer from '../../components/organisms/RebalanceDrawer'
import PortfolioTab from './tabs/PortfolioTab'
import RiskTab from './tabs/RiskTab'
import OpportunitiesTab from './tabs/OpportunitiesTab'
import AssetProfileTab from './tabs/AssetProfileTab'

export default function PortfolioPage() {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [rebalanceOpen, setRebalanceOpen] = useState(false)
  const { selectedTickers, selectedTags } = useAppStore()

  const { data: summary, isLoading } = usePortfolioSummary()

  const availableTags = (summary?.available_tags as string[]) ?? []

  // Filter asset table rows by selected tags (client-side)
  const allRows = useMemo(() => {
    const rows = (summary?.asset_table?.rows as Record<string, unknown>[]) ?? []
    if (!selectedTags.length) return rows
    return rows.filter((r) => {
      const tags = (r.tags as string[]) ?? []
      return selectedTags.some((t) => tags.includes(t))
    })
  }, [summary, selectedTags])

  // The first selected ticker's full row for the Asset Profile tab
  const selectedAssetRow = useMemo(() => {
    if (!selectedTickers.length) return undefined
    return allRows.find((r) => r.ticker === selectedTickers[0])
  }, [selectedTickers, allRows])

  const tabs = [
    { label: 'Portfolio', content: <PortfolioTab data={summary} /> },
    { label: 'Risk', content: <RiskTab data={summary} /> },
    { label: 'Opportunities', content: <OpportunitiesTab data={summary} /> },
    { label: 'Asset Profile', content: <AssetProfileTab assetRow={selectedAssetRow} /> },
  ]

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Navbar onSettingsOpen={() => setSettingsOpen(true)} onRebalanceOpen={() => setRebalanceOpen(true)} />

      {isLoading && <LinearProgress sx={{ height: 2 }} />}

      <Box sx={{ px: 1.5, pt: 1 }}>
        <KpiRow kpi={summary?.kpi as Record<string, unknown>} loading={isLoading} />
        <FilterBar availableTags={availableTags} />
      </Box>

      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', mt: 1 }}>
        <WorkspaceSplit
          left={
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <StatusBar />
              <Box sx={{ flex: 1, overflow: 'hidden' }}>
                <AssetTable rows={allRows} loading={isLoading} />
              </Box>
            </Box>
          }
          right={<WorkspaceTabs tabs={tabs} />}
        />
      </Box>

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <RebalanceDrawer open={rebalanceOpen} onClose={() => setRebalanceOpen(false)} />
    </Box>
  )
}
