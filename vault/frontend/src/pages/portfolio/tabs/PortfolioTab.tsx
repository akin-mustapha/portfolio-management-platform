import { useState, useMemo } from "react";
import { Box, useTheme } from "@mui/material";
import { usePortfolioContext } from "../PortfolioContext";
import ValueChart, {
  RangeSelector,
} from "../../../components/charts/design/ValueChart";
import DonutChart from "../../../components/charts/design/DonutChart";
import HoldingsTable from "../components/HoldingsTable";
import MoversCard from "../components/MoversCard";
import {
  Delta,
  fmtEUR,
  fmtPct,
} from "../../../components/charts/design/DesignPrimitives";
import type { SeriesPoint } from "../../../components/charts/design/ValueChart";
import type { SectorSlice } from "../../../components/charts/design/DonutChart";
import type { KpiVM } from "../../../presenters/portfolioPresenter";

function KpiStrip({ kpi }: { kpi: KpiVM }) {
  const theme = useTheme();
  if (!kpi) return null;
  const sym = kpi.currency_symbol ?? "€";
  const cells = [
    { label: "Invested", value: fmtEUR(kpi.total_cost), sub: "cost basis" },
    {
      label: "Unrealized P&L",
      value: fmtEUR(kpi.unrealized_pnl),
      color:
        kpi.unrealized_pnl >= 0
          ? theme.palette.success.main
          : theme.palette.error.main,
      sub:
        fmtPct((kpi.unrealized_pnl / (kpi.total_cost || 1)) * 100) + " on cost",
    },
    {
      label: "Cash available",
      value: sym + kpi.cash.toFixed(2),
      sub: sym + kpi.cash_reserved.toFixed(2) + " reserved",
    },
    {
      label: "vs S&P 500",
      value:
        kpi.portfolio_vs_benchmark_30d != null
          ? fmtPct(kpi.portfolio_vs_benchmark_30d)
          : "—",
      color:
        (kpi.portfolio_vs_benchmark_30d ?? 0) >= 0
          ? theme.palette.success.main
          : theme.palette.error.main,
      sub: `Sharpe ${kpi.sharpe_ratio_30d?.toFixed(2) ?? "—"} · β ${kpi.portfolio_beta?.toFixed(2) ?? "—"}`,
    },
  ];
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 12,
        background: theme.palette.background.paper,
        margin: "24px 32px 0",
      }}
    >
      {cells.map((c, i) => (
        <div
          key={i}
          style={{
            padding: "14px 18px",
            borderRight:
              i < cells.length - 1
                ? `1px solid ${theme.palette.divider}`
                : "none",
          }}
        >
          <div
            style={{
              fontSize: 10.5,
              fontWeight: 600,
              letterSpacing: ".08em",
              textTransform: "uppercase",
              color: theme.palette.text.secondary,
            }}
          >
            {c.label}
          </div>
          <div
            style={{
              fontSize: 22,
              fontWeight: 600,
              marginTop: 6,
              fontVariantNumeric: "tabular-nums",
              letterSpacing: "-0.02em",
              color: c.color ?? theme.palette.text.primary,
            }}
          >
            {c.value}
          </div>
          {c.sub && (
            <div
              style={{
                fontSize: 11.5,
                marginTop: 4,
                color: theme.palette.text.secondary,
              }}
            >
              {c.sub}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

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

function buildSectors(
  summary: NonNullable<ReturnType<typeof usePortfolioContext>["summary"]>,
): SectorSlice[] {
  const rows = summary.asset_table.rows;
  const totalValue = rows.reduce((s, r) => s + (Number(r.value) || 0), 0);
  const map: Record<string, number> = {};
  rows.forEach((r) => {
    const sector = r.sector ?? r.tags?.[0] ?? "Other";
    map[sector] = (map[sector] ?? 0) + (Number(r.value) || 0);
  });
  return Object.entries(map)
    .map(([sector, value]) => ({
      sector,
      value,
      weight: totalValue > 0 ? value / totalValue : 0,
    }))
    .sort((a, b) => b.value - a.value);
}

export default function PortfolioTab() {
  const { summary } = usePortfolioContext();
  const theme = useTheme();
  const [range, setRange] = useState("6M");
  const [search, setSearch] = useState("");
  const [sectorFilter, setSectorFilter] = useState("All");

  const series = useMemo(
    () => (summary ? buildSeries(summary) : []),
    [summary],
  );
  const sectors = useMemo(
    () => (summary ? buildSectors(summary) : []),
    [summary],
  );
  const sectorOptions = useMemo(
    () => ["All", ...sectors.map((s) => s.sector)],
    [sectors],
  );

  if (!summary) return null;
  const { kpi, asset_table, daily_movers } = summary;
  const sym = kpi.currency_symbol ?? "€";

  const topWinners = [...daily_movers]
    .sort((a, b) => b.daily_value_return - a.daily_value_return)
    .slice(0, 5);
  const topLosers = [...daily_movers]
    .sort((a, b) => a.daily_value_return - b.daily_value_return)
    .slice(0, 5);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1.6fr 1fr",
        height: "calc(100vh - 56px)",
      }}
    >
      {/* LEFT — hero + table */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          borderRight: `1px solid ${theme.palette.divider}`,
          overflow: "hidden",
        }}
      >
        {/* Hero */}
        <div style={{ padding: "32px 32px 0" }}>
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: ".1em",
              textTransform: "uppercase",
              color: theme.palette.text.secondary,
            }}
          >
            Portfolio value · as of {new Date().toISOString().slice(0, 10)}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 14,
              marginTop: 8,
              flexWrap: "wrap",
            }}
          >
            <span
              style={{
                fontSize: 48,
                fontWeight: 700,
                letterSpacing: "-0.035em",
                fontVariantNumeric: "tabular-nums",
                color: theme.palette.text.primary,
              }}
            >
              {sym}
              {kpi.value.toLocaleString("en-IE", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
            {kpi.daily_value_change_pct != null && (
              <Delta value={kpi.daily_value_change_pct} />
            )}
            <span style={{ fontSize: 12, color: theme.palette.text.secondary }}>
              today
            </span>
            <span style={{ flex: 1 }} />
            <Delta
              value={(kpi.unrealized_pnl / (kpi.total_cost || 1)) * 100}
              suffix="% all-time"
            />
          </div>
        </div>

        <div style={{ padding: "0 32px" }}>
          <ValueChart series={series} range={range} height={180} />
          <RangeSelector range={range} onChange={setRange} />
        </div>

        <KpiStrip kpi={kpi} />

        {/* Holdings header */}
        <div
          style={{
            padding: "20px 32px 0",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span style={{ fontSize: 14, fontWeight: 600 }}>
            Holdings{" "}
            <span
              style={{ color: theme.palette.text.secondary, fontWeight: 400 }}
            >
              · {asset_table.rows.length}
            </span>
          </span>
          <span style={{ flex: 1 }} />
          <div style={{ position: "relative" }}>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search ticker or name"
              style={{
                padding: "6px 10px 6px 30px",
                fontSize: 12.5,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: 7,
                background: theme.palette.background.paper,
                color: theme.palette.text.primary,
                outline: "none",
                width: 220,
              }}
            />
            <svg
              style={{
                position: "absolute",
                left: 9,
                top: "50%",
                transform: "translateY(-50%)",
                color: theme.palette.text.secondary,
                pointerEvents: "none",
              }}
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <path d="M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm10 2-4.3-4.3" />
            </svg>
          </div>
          <select
            value={sectorFilter}
            onChange={(e) => setSectorFilter(e.target.value)}
            style={{
              padding: "6px 28px 6px 10px",
              fontSize: 12.5,
              width: 90,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 7,
              background: theme.palette.background.paper,
              color: theme.palette.text.primary,
              outline: "none",
              appearance: "none",
              cursor: "pointer",
              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
              backgroundRepeat: "no-repeat",
              backgroundPosition: "right 8px center",
            }}
          >
            {sectorOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <Box
          sx={{
            flex: 1,
            minHeight: 0,
            mx: "32px",
            mb: "32px",
            mt: "12px",
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: "12px",
            bgcolor: "background.paper",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <HoldingsTable
            rows={asset_table.rows}
            search={search}
            sector={sectorFilter}
          />
        </Box>
      </div>

      {/* RIGHT — donut + movers */}
      <div
        style={{ display: "flex", flexDirection: "column", overflow: "auto" }}
      >
        <section style={{ padding: "32px 28px 0" }}>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              marginBottom: 14,
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: 14,
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              Sector allocation
            </h3>
            <span style={{ fontSize: 11, color: theme.palette.text.secondary }}>
              {asset_table.rows.length} holdings · {sectors.length} sectors
            </span>
          </div>
          <div
            style={{
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 12,
              padding: 20,
              background: theme.palette.background.paper,
            }}
          >
            <DonutChart
              sectors={sectors}
              holdingsCount={asset_table.rows.length}
              size={160}
              thick={22}
            />
          </div>
        </section>

        <section style={{ padding: "24px 28px 32px" }}>
          <h3
            style={{
              margin: "0 0 14px",
              fontSize: 14,
              fontWeight: 600,
              color: theme.palette.text.primary,
            }}
          >
            Today's movers
          </h3>
          <div
            style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}
          >
            <MoversCard title="Winners" items={topWinners} />
            <MoversCard title="Losers" items={topLosers} />
          </div>
        </section>
      </div>
    </div>
  );
}
