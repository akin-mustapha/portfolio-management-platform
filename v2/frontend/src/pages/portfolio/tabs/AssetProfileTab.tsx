import { Box, Typography, Stack } from '@mui/material'
import { useAssetHistory } from '../../../hooks/useAssetHistory'
import { useAppStore } from '../../../store/useAppStore'
import AssetPriceChart from '../../../components/charts/AssetPriceChart'
import AssetValueChart from '../../../components/charts/AssetValueChart'
import AssetPnlChart from '../../../components/charts/AssetPnlChart'
import AssetReturnChart from '../../../components/charts/AssetReturnChart'
import Section from '../../../components/molecules/Section'
import KpiGroup from '../../../components/molecules/KpiGroup'
import { usePortfolioContext } from '../PortfolioContext'
import { presentAssetKpis } from '../../../presenters/assetPresenter'

export default function AssetProfileTab() {
  const { selectedAssetRow: assetRow } = usePortfolioContext()
  const { fromDate, toDate } = useAppStore()

  const ticker = assetRow?.ticker as string | undefined

  const { data: history, isLoading } = useAssetHistory(ticker ?? null, fromDate ?? undefined, toDate ?? undefined)

  if (!ticker) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Select an asset in the table to view its profile.
        </Typography>
      </Box>
    )
  }

  const kpis = presentAssetKpis(assetRow as Record<string, unknown>)

  return (
    <Box sx={{ animation: 'fadeIn 220ms ease', '@keyframes fadeIn': { from: { opacity: 0 }, to: { opacity: 1 } } }}>
      <Stack spacing={1.5} sx={{ mb: 3 }}>
        <KpiGroup label="Performance" cards={kpis.performance} overflow="wrap" dimmed={false} />
        <KpiGroup label="Risk" cards={kpis.risk} overflow="wrap" dimmed={false} />
        <KpiGroup label="Allocation" cards={kpis.allocation} overflow="wrap" dimmed={false} />
      </Stack>

      {!isLoading && history && (
        <Stack spacing={1.5}>
          <Section title="Price + Moving Averages" metricKey="asset_price_chart">
            <AssetPriceChart series={history.asset_price} />
          </Section>
          <Section title="Asset Value" metricKey="asset_value_chart">
            <AssetValueChart series={history.asset_value} title="Value" />
          </Section>
          <Section title="P&L Range" metricKey="asset_profit_range_chart">
            <AssetPnlChart series={history.asset_profit_range} />
          </Section>
          <Section title="Cumulative Return" metricKey="asset_vs_portfolio_return_chart">
            <AssetReturnChart cumulativeSeries={history.asset_return} />
          </Section>
        </Stack>
      )}
    </Box>
  )
}
