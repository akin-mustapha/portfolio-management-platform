import { Box, Grid, Typography } from '@mui/material'
import Section from '../../../components/molecules/Section'
import PortfolioValueChart from '../../../components/charts/PortfolioValueChart'
import PortfolioPnlChart from '../../../components/charts/PortfolioPnlChart'
import PositionWeightChart from '../../../components/charts/PositionWeightChart'
import WinnersChart from '../../../components/charts/WinnersChart'
import LosersChart from '../../../components/charts/LosersChart'
import DailyMoversTable from '../../../components/charts/DailyMoversTable'
import { usePortfolioContext } from '../PortfolioContext'

export default function PortfolioTab() {
  const { summary: data } = usePortfolioContext()
  if (!data) return null

  return (
    <div>
      <Section title="Portfolio Value & P&L" metricKey="portfolio_value_chart">
        <PortfolioValueChart
          valueSeries={data.portfolio_value_series as Parameters<typeof PortfolioValueChart>[0]['valueSeries']}
          pnlSeries={data.portfolio_pnl_series as Parameters<typeof PortfolioValueChart>[0]['pnlSeries']}
        />
      </Section>

      {/* Container query wrapper — breakpoint is container width, not viewport */}
      <Box sx={{ containerType: 'inline-size', mb: 1 }}>
        <Box
          sx={{
            display: 'flex',
            gap: 1,
            alignItems: 'stretch',
            flexDirection: 'row',
            '@container (max-width: 900px)': { flexDirection: 'column' },
          }}
        >
          <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
            <Section title="Position Weights" metricKey="position_weight_chart" sx={{ flex: 1, mb: 0 }}>
              <PositionWeightChart distribution={data.position_distribution as Parameters<typeof PositionWeightChart>[0]['distribution']} />
            </Section>
          </Box>
          <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
            <Section title="Daily Movers" sx={{ flex: 1, mb: 0 }}>
              <DailyMoversTable movers={data.daily_movers as Parameters<typeof DailyMoversTable>[0]['movers']} />
            </Section>
          </Box>
        </Box>
      </Box>

      <Section title="Winners & Losers">
        <Grid container spacing={1}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">Top Winners</Typography>
            <WinnersChart winners={data.winners as Parameters<typeof WinnersChart>[0]['winners']} />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">Top Losers</Typography>
            <LosersChart losers={data.losers as Parameters<typeof LosersChart>[0]['losers']} />
          </Grid>
        </Grid>
      </Section>
    </div>
  )
}
