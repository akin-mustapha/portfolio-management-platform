import { Box, Typography } from '@mui/material'
import WinnersChart from '../../../components/charts/WinnersChart'
import LosersChart from '../../../components/charts/LosersChart'
import PositionPerformanceMap from '../../../components/charts/PositionPerformanceMap'
import OpportunitiesChart from '../../../components/charts/OpportunitiesChart'
import { useAppStore } from '../../../store/useAppStore'
import MetricInfo from '../../../components/atoms/MetricInfo'

interface OpportunitiesTabProps {
  data?: Record<string, unknown>
}

export default function OpportunitiesTab({ data }: OpportunitiesTabProps) {
  const { selectedTickers } = useAppStore()

  if (!data) return null

  // Opportunities tab shows winners sorted by value (potential), losers sorted by pnl_pct
  const winners = data.winners as Parameters<typeof WinnersChart>[0]['winners']
  const losers = data.losers as Parameters<typeof LosersChart>[0]['losers']
  const distribution = data.position_distribution as Parameters<typeof PositionPerformanceMap>[0]['distribution']
  const currencySymbol = (data.kpi as Record<string, unknown>)?.currency_symbol as string

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Box>
        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          Weight vs. Return Opportunity Map
        </Typography>
        <OpportunitiesChart distribution={distribution} />
      </Box>

      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
          <Typography variant="subtitle2" fontWeight={600}>
            Position Performance Map
          </Typography>
          <MetricInfo metricKey="position_performance_map_chart" />
        </Box>
        <PositionPerformanceMap
          distribution={distribution}
          currencySymbol={currencySymbol}
          selectedTickers={selectedTickers}
        />
      </Box>
      <Box>
        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          Best Performing Positions
        </Typography>
        <WinnersChart winners={winners} />
      </Box>
      <Box>
        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          Re-entry Candidates (Current Underperformers)
        </Typography>
        <LosersChart losers={losers} />
      </Box>
    </Box>
  )
}
