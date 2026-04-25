import { useCallback, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Box, LinearProgress } from '@mui/material'
import Navbar from '../../components/organisms/Navbar'
import KpiRow from '../../components/molecules/KpiRow'
import FilterBar from '../../components/molecules/FilterBar'
import AssetTable from '../../components/organisms/AssetTable'
import WorkspaceSplit from '../../components/organisms/WorkspaceSplit'
import SettingsModal from '../../components/organisms/SettingsModal'
import RebalanceDrawer from '../../components/organisms/RebalanceDrawer'
import AssetProfileDrawer from '../../components/organisms/AssetProfileDrawer'
import { PortfolioProvider, usePortfolioContext } from './PortfolioContext'
import { useAppStore } from '../../store/useAppStore'

function ShellInner({
  onSettingsOpen,
  onRebalanceOpen,
  profileOpen,
  onProfileToggle,
  onProfileOpen,
  onProfileClose,
}: {
  onSettingsOpen: () => void
  onRebalanceOpen: () => void
  profileOpen: boolean
  onProfileToggle: () => void
  onProfileOpen: (ticker: string) => void
  onProfileClose: () => void
}) {
  const { summary, loading, allRows, availableTags } = usePortfolioContext()

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Navbar
        onSettingsOpen={onSettingsOpen}
        onRebalanceOpen={onRebalanceOpen}
        onProfileToggle={onProfileToggle}
        profileOpen={profileOpen}
      />

      {loading && <LinearProgress sx={{ height: 2 }} />}

      <Box sx={{ px: 1.5, pt: 1 }}>
        <KpiRow
          kpi={summary?.kpi as Record<string, unknown>}
          valueSeries={summary?.portfolio_value_series as { values?: number[]; costs?: number[] } | undefined}
          pnlSeries={summary?.portfolio_pnl_series as { values?: number[] } | undefined}
          loading={loading}
        />
        <FilterBar />
      </Box>

      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'row', mt: 1 }}>
        <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
          <WorkspaceSplit
            left={
              <Box
                sx={(theme) => ({
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  mx: 1.5,
                  mt: 3,
                  mb: 1,
                  overflow: 'hidden',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 3,
                  bgcolor: 'background.paper',
                  boxShadow: theme.custom.shadowCard,
                })}
              >
                <AssetTable
                  rows={allRows}
                  loading={loading}
                  availableTags={availableTags}
                  onOpenDetails={onProfileOpen}
                />
              </Box>
            }
            right={
              <Box sx={{ height: '100%', overflow: 'auto', p: 1 }}>
                <Outlet />
              </Box>
            }
          />
        </Box>
        <AssetProfileDrawer open={profileOpen} onClose={onProfileClose} />
      </Box>
    </Box>
  )
}

export default function AppShell() {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [rebalanceOpen, setRebalanceOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const setSelectedTickers = useAppStore((s) => s.setSelectedTickers)

  const handleSettingsOpen = useCallback(() => setSettingsOpen(true), [])
  const handleSettingsClose = useCallback(() => setSettingsOpen(false), [])
  const handleRebalanceOpen = useCallback(() => setRebalanceOpen(true), [])
  const handleRebalanceClose = useCallback(() => setRebalanceOpen(false), [])
  const handleProfileToggle = useCallback(() => setProfileOpen((v) => !v), [])
  const handleProfileClose = useCallback(() => setProfileOpen(false), [])
  const handleProfileOpen = useCallback(
    (ticker: string) => {
      setSelectedTickers([ticker])
      setProfileOpen(true)
    },
    [setSelectedTickers],
  )

  return (
    <PortfolioProvider>
      <ShellInner
        onSettingsOpen={handleSettingsOpen}
        onRebalanceOpen={handleRebalanceOpen}
        profileOpen={profileOpen}
        onProfileToggle={handleProfileToggle}
        onProfileOpen={handleProfileOpen}
        onProfileClose={handleProfileClose}
      />
      <SettingsModal open={settingsOpen} onClose={handleSettingsClose} />
      <RebalanceDrawer open={rebalanceOpen} onClose={handleRebalanceClose} />
    </PortfolioProvider>
  )
}
