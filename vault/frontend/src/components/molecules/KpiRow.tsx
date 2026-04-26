import { Box } from "@mui/material";
import KpiCard from "../atoms/KpiCard";
import KpiGroup, { type KpiGroupItem } from "./KpiGroup";

interface KpiRowProps {
  kpi?: Record<string, unknown>;
  valueSeries?: { values?: number[]; costs?: number[] };
  pnlSeries?: { values?: number[] };
  loading?: boolean;
}

type CardDef = KpiGroupItem & {
  colorCode: "positive" | "negative" | "neutral";
};

export default function KpiRow({
  kpi,
  valueSeries,
  pnlSeries,
  loading = false,
}: KpiRowProps) {
  const symbol = (kpi?.currency_symbol as string) ?? "";
  const unrealizedPnl = kpi?.unrealized_pnl as number | undefined;
  const realizedPnl = kpi?.realized_pnl as number | undefined;
  const dailyChange = kpi?.daily_value_change_pct as number | undefined;

  const vsBenchmark = kpi?.portfolio_vs_benchmark_30d as number | undefined;

  const portfolioValue = kpi?.value as number | undefined;
  const heroSub =
    dailyChange != null
      ? `${dailyChange >= 0 ? "+" : ""}${dailyChange.toFixed(2)}% today`
      : undefined;

  const supportingCards: CardDef[] = [
    {
      label: "Total Invested",
      value: kpi?.total_cost as number | undefined,
      prefix: symbol,
      colorCode: "neutral",
      sparkline: valueSeries?.costs,
    },
    {
      label: "Unrealized P&L",
      value: unrealizedPnl,
      prefix: symbol,
      colorCode:
        unrealizedPnl != null
          ? unrealizedPnl >= 0
            ? "positive"
            : "negative"
          : "neutral",
      sparkline: pnlSeries?.values,
    },
    {
      label: "Realized P&L",
      value: realizedPnl,
      prefix: symbol,
      colorCode:
        realizedPnl != null
          ? realizedPnl >= 0
            ? "positive"
            : "negative"
          : "neutral",
    },
    {
      label: "Vol (weighted)",
      value: kpi?.portfolio_vol as number | undefined,
      suffix: "%",
      colorCode: "neutral",
      metricKey: "portfolio_volatility_30d",
    },
    {
      label: "Beta",
      value: kpi?.portfolio_beta as number | undefined,
      colorCode: "neutral",
      metricKey: "portfolio_beta",
    },
    {
      label: "Sharpe 30D",
      value: kpi?.sharpe_ratio_30d as number | undefined,
      colorCode:
        ((kpi?.sharpe_ratio_30d as number) ?? 0) >= 1 ? "positive" : "neutral",
      metricKey: "portfolio_sharpe_30d",
    },
    {
      label: "vs SP500 30D",
      value: vsBenchmark,
      suffix: "%",
      colorCode:
        vsBenchmark != null
          ? vsBenchmark >= 0
            ? "positive"
            : "negative"
          : "neutral",
      metricKey: "portfolio_vs_sp500_30d",
    },
  ];

  const cashCards: CardDef[] = [
    {
      label: "Cash Available",
      value: kpi?.cash as number | undefined,
      prefix: symbol,
      colorCode: "neutral",
    },
    {
      label: "Cash Reserved",
      value: kpi?.cash_reserved as number | undefined,
      prefix: symbol,
      colorCode: "neutral",
    },
    {
      label: "Cash in Pies",
      value: kpi?.cash_in_pies as number | undefined,
      prefix: symbol,
      colorCode: "neutral",
    },
  ];

  return (
    <Box
      sx={{
        display: "flex",
        gap: 1,
        alignItems: "stretch",
        mb: 1,
        flexWrap: "wrap",
      }}
    >
      <Box
        sx={(theme) => ({
          flex: "1.4 1 340px",
          minWidth: 0,
          display: "flex",
          position: "relative",
          borderRadius: 3,
          border: "1px solid",
          borderColor:
            theme.palette.mode === "dark"
              ? "rgba(107,140,255,0.32)"
              : "rgba(59,91,255,0.26)",
          bgcolor: "background.paper",
          boxShadow:
            theme.palette.mode === "dark"
              ? "0 1px 2px rgba(0,0,0,0.24), 0 12px 36px -12px rgba(107,140,255,0.32)"
              : "0 1px 2px rgba(15,23,42,0.04), 0 12px 36px -14px rgba(59,91,255,0.28)",
          overflow: "hidden",
          "&::before": {
            content: '""',
            position: "absolute",
            inset: 0,
            background:
              theme.palette.mode === "dark"
                ? "radial-gradient(130% 90% at 0% 0%, rgba(107,140,255,0.18) 0%, rgba(107,140,255,0) 60%)"
                : "radial-gradient(130% 90% at 0% 0%, rgba(59,91,255,0.14) 0%, rgba(59,91,255,0) 60%)",
            pointerEvents: "none",
          },
          transition: "box-shadow 180ms ease, border-color 180ms ease",
        })}
      >
        <Box sx={{ flex: 1 }}>
          <KpiCard
            variant="hero"
            label="Portfolio Value"
            value={portfolioValue}
            prefix={symbol}
            subValue={heroSub}
            colorCode={
              dailyChange != null
                ? dailyChange >= 0
                  ? "positive"
                  : "negative"
                : "neutral"
            }
            sparkline={valueSeries?.values}
            loading={loading}
          />
        </Box>
      </Box>

      <Box sx={{ flex: "3 1 560px", minWidth: 0, display: "flex" }}>
        <KpiGroup
          label="Performance"
          cards={supportingCards}
          loading={loading}
        />
      </Box>
      <Box sx={{ flex: "1 1 240px", minWidth: 0, display: "flex" }}>
        <KpiGroup label="Cash" cards={cashCards} loading={loading} />
      </Box>
    </Box>
  );
}
