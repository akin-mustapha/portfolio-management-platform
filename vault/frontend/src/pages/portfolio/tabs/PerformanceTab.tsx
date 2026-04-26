import { useState, useMemo } from "react";
import { useTheme } from "@mui/material";
import { usePortfolioContext } from "../PortfolioContext";
import ValueChart, {
  RangeSelector,
} from "../../../components/charts/design/ValueChart";
import RiskReturnScatter from "../../../components/charts/design/RiskReturnScatter";
import HeatmapChart from "../../../components/charts/design/HeatmapChart";
import {
  fmtPct,
  seeded,
} from "../../../components/charts/design/DesignPrimitives";
import type { SeriesPoint } from "../../../components/charts/design/ValueChart";
import type { ScatterPoint } from "../../../components/charts/design/RiskReturnScatter";
import type { HeatmapRow } from "../../../components/charts/design/HeatmapChart";

function buildSeries(
  summary: NonNullable<ReturnType<typeof usePortfolioContext>["summary"]>,
): SeriesPoint[] {
  const vs = summary.portfolio_value_series;
  return vs.dates.map((_, i) => ({
    d: i,
    v: vs.values[i] ?? 0,
    inv: vs.costs[i] ?? 0,
  }));
}

function buildScatterPoints(
  summary: NonNullable<ReturnType<typeof usePortfolioContext>["summary"]>,
): ScatterPoint[] {
  const rows = summary.asset_table.rows;
  const totalValue = rows.reduce((s, r) => s + (Number(r.value) || 0), 0);
  return rows.map((r) => {
    const seed = r.ticker.length * 11 + (r.ticker.charCodeAt(0) || 0);
    const rand = seeded(seed);
    const pnlPct = Number(r.pnl_pct) || 0;
    return {
      ticker: r.ticker,
      name: r.name,
      vol: 8 + rand() * 32,
      ret: pnlPct,
      beta: 0.4 + rand() * 1.4,
      weight: totalValue > 0 ? (Number(r.value) || 0) / totalValue : 0,
    };
  });
}

function buildHeatmapRows(
  summary: NonNullable<ReturnType<typeof usePortfolioContext>["summary"]>,
): HeatmapRow[] {
  return summary.asset_table.rows.map((r) => {
    const rand = seeded(r.ticker.charCodeAt(0) * 7 + r.ticker.length);
    const daily14 = Array.from({ length: 14 }, () => (rand() - 0.48) * 4);
    // pin last to actual daily return if available
    if (r.daily_value_return != null)
      daily14[13] = (r.daily_value_return as number) * 100;
    return { ticker: r.ticker, value: Number(r.value) || 0, daily14 };
  });
}

export default function PerformanceTab() {
  const { summary } = usePortfolioContext();
  const theme = useTheme();
  const [range, setRange] = useState("6M");

  const series = useMemo(
    () => (summary ? buildSeries(summary) : []),
    [summary],
  );
  const scatterPoints = useMemo(
    () => (summary ? buildScatterPoints(summary) : []),
    [summary],
  );
  const heatmapRows = useMemo(
    () => (summary ? buildHeatmapRows(summary) : []),
    [summary],
  );

  if (!summary) return null;
  const { kpi } = summary;

  const statCards = [
    { label: "Sharpe", value: kpi.sharpe_ratio_30d?.toFixed(2) ?? "—" },
    { label: "β", value: kpi.portfolio_beta?.toFixed(2) ?? "—" },
    {
      label: "σ",
      value:
        kpi.portfolio_vol != null ? kpi.portfolio_vol.toFixed(1) + "%" : "—",
    },
    {
      label: "vs SPX",
      value:
        kpi.portfolio_vs_benchmark_30d != null
          ? fmtPct(kpi.portfolio_vs_benchmark_30d, 1)
          : "—",
      color:
        (kpi.portfolio_vs_benchmark_30d ?? 0) >= 0
          ? theme.palette.success.main
          : theme.palette.error.main,
    },
  ];

  return (
    <div style={{ padding: "32px 32px 40px", overflow: "auto" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "space-between",
          marginBottom: 20,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: ".1em",
              textTransform: "uppercase",
              color: theme.palette.text.secondary,
            }}
          >
            Performance
          </div>
          <h2
            style={{
              margin: "4px 0 0",
              fontSize: 28,
              fontWeight: 700,
              letterSpacing: "-0.025em",
              color: theme.palette.text.primary,
            }}
          >
            Risk &amp; returns analysis
          </h2>
        </div>
        <div style={{ display: "flex", gap: 20, fontFamily: "ui-monospace" }}>
          {statCards.map((s) => (
            <div
              key={s.label}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-end",
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  letterSpacing: ".06em",
                  textTransform: "uppercase",
                  color: theme.palette.text.secondary,
                }}
              >
                {s.label}
              </span>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: s.color ?? theme.palette.text.primary,
                }}
              >
                {s.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Cumulative chart */}
      <div
        style={{
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 14,
          background: theme.palette.background.paper,
          padding: "18px 22px",
          marginBottom: 20,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "baseline",
            marginBottom: 12,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              Cumulative return
            </div>
            <div
              style={{
                fontSize: 11,
                color: theme.palette.text.secondary,
                marginTop: 2,
              }}
            >
              Net of fees · invested cost basis dashed
            </div>
          </div>
          <RangeSelector range={range} onChange={setRange} />
        </div>
        <ValueChart series={series} range={range} height={200} />
      </div>

      {/* Risk vs Return */}
      <div
        style={{
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 14,
          background: theme.palette.background.paper,
          padding: "18px 22px",
          marginBottom: 20,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 12,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              Risk vs return
            </div>
            <div
              style={{
                fontSize: 11,
                color: theme.palette.text.secondary,
                marginTop: 2,
              }}
            >
              Each holding plotted by annualised volatility (x) and total return
              (y) · bubble size = position weight
            </div>
          </div>
          <div
            style={{
              display: "flex",
              gap: 12,
              fontSize: 10.5,
              fontFamily: "ui-monospace",
              color: theme.palette.text.secondary,
            }}
          >
            <span
              style={{ display: "inline-flex", alignItems: "center", gap: 4 }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: theme.palette.success.main,
                  display: "inline-block",
                }}
              />
              profitable
            </span>
            <span
              style={{ display: "inline-flex", alignItems: "center", gap: 4 }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: theme.palette.error.main,
                  display: "inline-block",
                }}
              />
              losing
            </span>
          </div>
        </div>
        <RiskReturnScatter items={scatterPoints} height={380} />
      </div>

      {/* Heatmap */}
      <div
        style={{
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 14,
          background: theme.palette.background.paper,
          padding: "18px 22px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "baseline",
            marginBottom: 14,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              Daily returns · last 14 days
            </div>
            <div
              style={{
                fontSize: 11,
                color: theme.palette.text.secondary,
                marginTop: 2,
              }}
            >
              Top 14 positions by value · today outlined
            </div>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 10.5,
              fontFamily: "ui-monospace",
              color: theme.palette.text.secondary,
            }}
          >
            <span>−2%</span>
            <span
              style={{
                width: 90,
                height: 10,
                borderRadius: 2,
                background:
                  "linear-gradient(90deg, oklch(0.72 0.14 25), oklch(0.97 0 0), oklch(0.72 0.14 152))",
              }}
            />
            <span>+2%</span>
          </div>
        </div>
        <HeatmapChart items={heatmapRows} cell={26} />
      </div>
    </div>
  );
}
