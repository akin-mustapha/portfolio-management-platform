import Section from '../../../components/molecules/Section'
import { DrawdownChart } from '../../../components/charts/portfolio'
import { ProfitabilityChart } from '../../../components/charts/shared'
import { VarByPositionChart } from '../../../components/charts/position'
import { UnprofitablePnlChart } from '../../../components/charts/screener'
import { usePortfolioContext } from '../PortfolioContext'
import { presentProfitability } from '../../../presenters/riskPresenter'

export default function RiskTab() {
  const { summary: data } = usePortfolioContext()
  if (!data) return null

  const profitabilityVM = presentProfitability(data.profitability)

  return (
    <div>
      <Section title="Portfolio Drawdown" metricKey="portfolio_drawdown_chart">
        <DrawdownChart drawdown={data.portfolio_drawdown} />
      </Section>

      <Section title="Profitability Distribution" metricKey="position_profitability_chart">
        <ProfitabilityChart vm={profitabilityVM} />
      </Section>

      <Section title="VaR by Position" metricKey="var_by_position_chart">
        <VarByPositionChart varData={data.var_by_position} />
      </Section>

      <Section title="Unprofitable Positions P&L">
        <UnprofitablePnlChart losersData={data.losers_pnl} />
      </Section>
    </div>
  )
}
