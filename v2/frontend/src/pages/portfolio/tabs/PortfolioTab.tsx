import { Box, Grid, Typography } from '@mui/material'
import Section from '../../../components/molecules/Section'
import PortfolioValueChart from '../../../components/charts/PortfolioValueChart'
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
        <PortfolioValueChart rows={data.portfolio_value_chart_rows} />
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
              <PositionWeightChart top10={data.position_weight_top10} />
            </Section>
          </Box>
          <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
            <Section title="Daily Movers" sx={{ flex: 1, mb: 0 }}>
              <DailyMoversTable movers={data.daily_movers} />
            </Section>
          </Box>
        </Box>
      </Box>

      <Section title="Winners & Losers">
        <Grid container spacing={1}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">Top Winners</Typography>
            <WinnersChart winners={data.winners} />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">Top Losers</Typography>
            <LosersChart losers={data.losers} />
          </Grid>
        </Grid>
      </Section>
    </div>
  )
}
