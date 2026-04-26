import { Box, Typography, Stack } from "@mui/material";
import { useAssetHistory } from "../../../hooks/useAssetHistory";
import { useAppStore } from "../../../store/useAppStore";
import AssetPriceChart from "../../../components/charts/AssetPriceChart";
import AssetValueChart from "../../../components/charts/AssetValueChart";
import AssetPnlChart from "../../../components/charts/AssetPnlChart";
import AssetReturnChart from "../../../components/charts/AssetReturnChart";
import TickerLogo from "../../../components/atoms/TickerLogo";
import Section from "../../../components/molecules/Section";
import KpiGroup, {
  type KpiGroupItem,
} from "../../../components/molecules/KpiGroup";
import { usePortfolioContext } from "../PortfolioContext";

type KpiDef = KpiGroupItem;

export default function AssetProfileTab() {
  const { selectedAssetRow: assetRow } = usePortfolioContext();
  const { fromDate, toDate } = useAppStore();

  const ticker = assetRow?.ticker as string | undefined;

  const { data: history, isLoading } = useAssetHistory(
    ticker ?? null,
    fromDate ?? undefined,
    toDate ?? undefined,
  );

  if (!ticker) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          Select an asset in the table to view its profile.
        </Typography>
      </Box>
    );
  }

  const profit = assetRow?.profit as number | undefined;
  const pnlPct = assetRow?.pnl_pct as number | undefined;

  const performanceKpis: KpiDef[] = [
    { label: "Value", value: assetRow?.value as number | undefined },
    {
      label: "P&L",
      value: profit,
      colorCode: (profit ?? 0) >= 0 ? "positive" : "negative",
      metricKey: "profit",
    },
    {
      label: "P&L %",
      value: pnlPct,
      suffix: "%",
      colorCode: (pnlPct ?? 0) >= 0 ? "positive" : "negative",
      metricKey: "pnl_pct",
    },
  ];

  const riskKpis: KpiDef[] = [
    {
      label: "Vol 30d",
      value: assetRow?.volatility_30d as number | undefined,
      metricKey: "volatility_30d",
    },
    {
      label: "VaR 95%",
      value: assetRow?.var_95_1d as number | undefined,
      metricKey: "var_95_1d",
    },
    { label: "Beta 60d", value: assetRow?.beta_60d as number | undefined },
  ];

  const allocationKpis: KpiDef[] = [
    {
      label: "Weight",
      value: assetRow?.weight_pct as number | undefined,
      suffix: "%",
      metricKey: "weight_pct",
    },
    {
      label: "Avg Price",
      value: assetRow?.avg_price as number | undefined,
      metricKey: "avg_price",
    },
    { label: "Cost", value: assetRow?.cost as number | undefined },
  ];

  return (
    <Box
      sx={{
        animation: "fadeIn 220ms ease",
        "@keyframes fadeIn": { from: { opacity: 0 }, to: { opacity: 1 } },
      }}
    >
      <Stack spacing={1.5} sx={{ mb: 3 }}>
        <KpiGroup
          label="Performance"
          cards={performanceKpis}
          overflow="wrap"
          dimmed={false}
        />
        <KpiGroup
          label="Risk"
          cards={riskKpis}
          overflow="wrap"
          dimmed={false}
        />
        <KpiGroup
          label="Allocation"
          cards={allocationKpis}
          overflow="wrap"
          dimmed={false}
        />
      </Stack>

      {!isLoading && history && (
        <Stack spacing={1.5}>
          <Section
            title="Price + Moving Averages"
            metricKey="asset_price_chart"
          >
            <AssetPriceChart series={history.asset_price} />
          </Section>
          <Section title="Asset Value" metricKey="asset_value_chart">
            <AssetValueChart series={history.asset_value} title="Value" />
          </Section>
          <Section title="P&L Range" metricKey="asset_profit_range_chart">
            <AssetPnlChart series={history.asset_profit_range} />
          </Section>
          <Section
            title="Cumulative Return"
            metricKey="asset_vs_portfolio_return_chart"
          >
            <AssetReturnChart cumulativeSeries={history.asset_return} />
          </Section>
        </Stack>
      )}
    </Box>
  );
}
