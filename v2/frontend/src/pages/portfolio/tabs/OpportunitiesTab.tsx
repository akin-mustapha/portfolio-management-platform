import WinnersChart from '../../../components/charts/WinnersChart'
import LosersChart from '../../../components/charts/LosersChart'
import PositionPerformanceMap from '../../../components/charts/PositionPerformanceMap'
import OpportunitiesChart from '../../../components/charts/OpportunitiesChart'
import { useAppStore } from '../../../store/useAppStore'
import Section from '../../../components/molecules/Section'
import { usePortfolioContext } from '../PortfolioContext'
import {
  presentPerformanceMap,
  presentOpportunitiesChart,
} from '../../../presenters/opportunitiesPresenter'

export default function OpportunitiesTab() {
  const { summary: data } = usePortfolioContext()
  const { selectedTickers } = useAppStore()

  if (!data) return null

  const performanceMapVM = presentPerformanceMap(data.position_distribution, selectedTickers)
  const opportunitiesVM = presentOpportunitiesChart(data.position_distribution)

  return (
    <div>
      <Section title="Weight vs. Return Opportunity Map">
        <OpportunitiesChart vm={opportunitiesVM} />
      </Section>

      <Section title="Position Performance Map" metricKey="position_performance_map_chart">
        <PositionPerformanceMap
          vm={performanceMapVM}
          currencySymbol={data.kpi.currency_symbol}
        />
      </Section>

      <Section title="Best Performing Positions">
        <WinnersChart winners={data.winners} />
      </Section>

      <Section title="Re-entry Candidates (Current Underperformers)">
        <LosersChart losers={data.losers} />
      </Section>
    </div>
  )
}
