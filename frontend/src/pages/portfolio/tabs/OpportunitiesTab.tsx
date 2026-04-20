import WinnersChart from '../../../components/charts/WinnersChart'
import LosersChart from '../../../components/charts/LosersChart'
import PositionPerformanceMap from '../../../components/charts/PositionPerformanceMap'
import OpportunitiesChart from '../../../components/charts/OpportunitiesChart'
import { useAppStore } from '../../../store/useAppStore'
import Section from '../../../components/molecules/Section'
<<<<<<< HEAD
=======
import { usePortfolioContext } from '../PortfolioContext'
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223

export default function OpportunitiesTab() {
  const { summary: data } = usePortfolioContext()
  const { selectedTickers } = useAppStore()

  if (!data) return null

  // Opportunities tab shows winners sorted by value (potential), losers sorted by pnl_pct
  const winners = data.winners as Parameters<typeof WinnersChart>[0]['winners']
  const losers = data.losers as Parameters<typeof LosersChart>[0]['losers']
  const distribution = data.position_distribution as Parameters<typeof PositionPerformanceMap>[0]['distribution']
  const currencySymbol = (data.kpi as Record<string, unknown>)?.currency_symbol as string

  return (
    <div>
      <Section title="Weight vs. Return Opportunity Map">
        <OpportunitiesChart distribution={distribution} />
      </Section>

      <Section title="Position Performance Map" metricKey="position_performance_map_chart">
        <PositionPerformanceMap
          distribution={distribution}
          currencySymbol={currencySymbol}
          selectedTickers={selectedTickers}
        />
      </Section>

      <Section title="Best Performing Positions">
        <WinnersChart winners={winners} />
      </Section>

      <Section title="Re-entry Candidates (Current Underperformers)">
        <LosersChart losers={losers} />
      </Section>
    </div>
  )
}
