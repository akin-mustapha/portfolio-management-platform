import { Box, Chip, Typography, Divider, Button } from '@mui/material'
import { useState } from 'react'
import { useAssetHistory } from '../../../hooks/useAssetHistory'
import { useAppStore } from '../../../store/useAppStore'
import AssetPriceChart from '../../../components/charts/AssetPriceChart'
import AssetValueChart from '../../../components/charts/AssetValueChart'
import AssetPnlChart from '../../../components/charts/AssetPnlChart'
import AssetReturnChart from '../../../components/charts/AssetReturnChart'
import EditTagsModal from '../../../components/organisms/EditTagsModal'
import KpiCard from '../../../components/atoms/KpiCard'
import TickerLogo from '../../../components/atoms/TickerLogo'
import Section from '../../../components/molecules/Section'
import { Grid } from '@mui/material'

interface AssetProfileTabProps {
  assetRow?: Record<string, unknown>
}

export default function AssetProfileTab({ assetRow }: AssetProfileTabProps) {
  const [tagsOpen, setTagsOpen] = useState(false)
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

  const tags = (assetRow?.tags as string[]) ?? []

  return (
    <Box>
      {/* Header row */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, flexWrap: 'wrap' }}>
        <TickerLogo ticker={ticker} />
        <Typography variant="subtitle1" fontWeight={700}>{ticker}</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ flex: 1 }}>
          {assetRow?.name as string}
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {tags.map((t) => (
            <Chip key={t} label={t} size="small" variant="outlined" sx={{ fontSize: 10 }} />
          ))}
          <Button size="small" variant="outlined" sx={{ fontSize: 10, height: 22 }} onClick={() => setTagsOpen(true)}>
            Edit Tags
          </Button>
        </Box>
      </Box>

      {/* KPI mini row */}
      <Grid container spacing={1} sx={{ mb: 1 }}>
        {[
          { label: 'Value', value: assetRow?.value as number | undefined },
          { label: 'P&L', value: assetRow?.profit as number | undefined, colorCode: ((assetRow?.profit as number) ?? 0) >= 0 ? 'positive' : 'negative', metricKey: 'profit' },
          { label: 'P&L %', value: assetRow?.pnl_pct as number | undefined, suffix: '%', colorCode: ((assetRow?.pnl_pct as number) ?? 0) >= 0 ? 'positive' : 'negative', metricKey: 'pnl_pct' },
          { label: 'Weight', value: assetRow?.weight_pct as number | undefined, suffix: '%', metricKey: 'weight_pct' },
          { label: 'Vol 30d', value: assetRow?.volatility_30d as number | undefined, metricKey: 'volatility_30d' },
          { label: 'VaR 95%', value: assetRow?.var_95_1d as number | undefined, metricKey: 'var_95_1d' },
        ].map((c) => (
          <Grid key={c.label} size={{ xs: 6, sm: 4, md: 2 }}>
            <KpiCard {...(c as Parameters<typeof KpiCard>[0])} compact />
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ mb: 1 }} />

      {/* Charts */}
      {!isLoading && history && (
        <div>
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
        </div>
      )}

      <EditTagsModal
        open={tagsOpen}
        onClose={() => setTagsOpen(false)}
        ticker={ticker}
        currentTags={tags}
      />
    </Box>
  )
}
