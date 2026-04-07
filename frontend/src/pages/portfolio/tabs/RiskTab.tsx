import Section from '../../../components/molecules/Section'
import DrawdownChart from '../../../components/charts/DrawdownChart'
import ProfitabilityChart from '../../../components/charts/ProfitabilityChart'
import VarByPositionChart from '../../../components/charts/VarByPositionChart'
import UnprofitablePnlChart from '../../../components/charts/UnprofitablePnlChart'

interface RiskTabProps {
  data?: Record<string, unknown>
}

export default function RiskTab({ data }: RiskTabProps) {
  if (!data) return null

  return (
    <div>
      <Section title="Portfolio Drawdown" metricKey="portfolio_drawdown_chart">
        <DrawdownChart drawdown={data.portfolio_drawdown as Parameters<typeof DrawdownChart>[0]['drawdown']} />
      </Section>

      <Section title="Profitability Distribution" metricKey="position_profitability_chart">
        <ProfitabilityChart assets={data.profitability as Parameters<typeof ProfitabilityChart>[0]['assets']} />
      </Section>

      <Section title="VaR by Position" metricKey="var_by_position_chart">
        <VarByPositionChart varData={data.var_by_position as Parameters<typeof VarByPositionChart>[0]['varData']} />
      </Section>

      <Section title="Unprofitable Positions P&L">
        <UnprofitablePnlChart losersData={data.losers_pnl as Parameters<typeof UnprofitablePnlChart>[0]['losersData']} />
      </Section>
    </div>
  )
}
