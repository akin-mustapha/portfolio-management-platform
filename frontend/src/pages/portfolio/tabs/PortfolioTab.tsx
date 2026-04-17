import { Grid, Typography } from '@mui/material'
import Section from '../../../components/molecules/Section'
import PortfolioValueChart from '../../../components/charts/PortfolioValueChart'
import PortfolioPnlChart from '../../../components/charts/PortfolioPnlChart'
import PositionWeightChart from '../../../components/charts/PositionWeightChart'
import WinnersChart from '../../../components/charts/WinnersChart'
import LosersChart from '../../../components/charts/LosersChart'
import DailyMoversTable from '../../../components/charts/DailyMoversTable'

interface PortfolioTabProps {
  data?: Record<string, unknown>
}

export default function PortfolioTab({ data }: PortfolioTabProps) {
  if (!data) return null

  return (
    <div>
      <Section title="Portfolio Value" metricKey="portfolio_value_chart">
        <PortfolioValueChart series={data.portfolio_value_series as Parameters<typeof PortfolioValueChart>[0]['series']} />
      </Section>

      <Section title="P&L Over Time" metricKey="portfolio_pnl_chart">
        <PortfolioPnlChart series={data.portfolio_pnl_series as Parameters<typeof PortfolioPnlChart>[0]['series']} />
      </Section>

      <Section title="Position Weights" metricKey="position_weight_chart">
        <PositionWeightChart distribution={data.position_distribution as Parameters<typeof PositionWeightChart>[0]['distribution']} />
      </Section>

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

      <Section title="Daily Movers">
        <DailyMoversTable movers={data.daily_movers as Parameters<typeof DailyMoversTable>[0]['movers']} />
      </Section>
    </div>
  )
}
