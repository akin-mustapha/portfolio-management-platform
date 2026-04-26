import { useMemo, useRef, useEffect, useState } from "react";
import { useTheme } from "@mui/material";
import type { Theme } from "@mui/material";
import { usePortfolioContext } from "../PortfolioContext";
import {
  fmtEUR,
  fmtPct,
} from "../../../components/charts/design/DesignPrimitives";
import type { RawAsset } from "../../../presenters/portfolioPresenter";

// ─── Concentration / HHI gauge ────────────────────────────────────────────

function ConcentrationGauge({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme();
  const totalValue = assets.reduce((s, a) => s + (Number(a.value) || 0), 0);
  const weights = assets.map((a) => (Number(a.value) || 0) / (totalValue || 1));
  const hhi = weights.reduce((s, w) => s + (w * 100) ** 2, 0);
  const effN = 10000 / (hhi || 1);
  const norm = Math.min(1, hhi / 2500);

  const r = 95,
    cx = 130,
    cy = 110;
  const startA = Math.PI,
    endA = 2 * Math.PI;
  const a = startA + norm * (endA - startA);
  const ndx = cx + Math.cos(a) * r,
    ndy = cy + Math.sin(a) * r;

  const arc = (from: number, to: number, color: string) => {
    const x1 = cx + Math.cos(from) * r,
      y1 = cy + Math.sin(from) * r;
    const x2 = cx + Math.cos(to) * r,
      y2 = cy + Math.sin(to) * r;
    return (
      <path
        d={`M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`}
        stroke={color}
        strokeWidth="14"
        fill="none"
        strokeLinecap="round"
      />
    );
  };
  const seg1 = startA + (endA - startA) * 0.33;
  const seg2 = startA + (endA - startA) * 0.66;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
      <svg width={260} height={140} style={{ flexShrink: 0 }}>
        {arc(startA, seg1, "oklch(0.78 0.15 152)")}
        {arc(seg1, seg2, "oklch(0.82 0.13 80)")}
        {arc(seg2, endA, "oklch(0.72 0.18 25)")}
        <line
          x1={cx}
          y1={cy}
          x2={ndx}
          y2={ndy}
          stroke={theme.palette.text.primary}
          strokeWidth="2"
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="5" fill={theme.palette.text.primary} />
        <text
          x={cx - r - 4}
          y={cy + 16}
          fontSize="9.5"
          fill={theme.palette.text.secondary}
          fontFamily="ui-monospace"
          textAnchor="middle"
        >
          DIVERSIFIED
        </text>
        <text
          x={cx + r + 4}
          y={cy + 16}
          fontSize="9.5"
          fill={theme.palette.text.secondary}
          fontFamily="ui-monospace"
          textAnchor="middle"
        >
          CONCENTRATED
        </text>
      </svg>
      <div>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: ".08em",
            textTransform: "uppercase",
            color: theme.palette.text.secondary,
          }}
        >
          Concentration · HHI
        </div>
        <div
          style={{
            fontSize: 36,
            fontWeight: 700,
            letterSpacing: "-0.025em",
            fontVariantNumeric: "tabular-nums",
            marginTop: 4,
            color: theme.palette.text.primary,
          }}
        >
          {Math.round(hhi)}
        </div>
        <div
          style={{
            fontSize: 12,
            color: theme.palette.text.secondary,
            marginTop: 4,
            fontFamily: "ui-monospace",
          }}
        >
          Effective holdings:{" "}
          <span style={{ color: theme.palette.text.primary, fontWeight: 600 }}>
            {effN.toFixed(1)}
          </span>{" "}
          of {assets.length}
        </div>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            marginTop: 6,
            color:
              hhi < 1000
                ? theme.palette.success.main
                : hhi < 1800
                  ? "oklch(0.6 0.15 80)"
                  : theme.palette.error.main,
          }}
        >
          {hhi < 1000
            ? "✓ Well diversified"
            : hhi < 1800
              ? "! Moderately concentrated"
              : "× Highly concentrated"}
        </div>
      </div>
    </div>
  );
}

// ─── Top-5 weight bar ─────────────────────────────────────────────────────

function TopFiveBar({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme();
  const totalValue = assets.reduce((s, a) => s + (Number(a.value) || 0), 0);
  const sorted = [...assets]
    .map((a) => ({
      ticker: a.ticker,
      name: a.name,
      weight: (Number(a.value) || 0) / (totalValue || 1),
    }))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 5);
  const topPct = sorted.reduce((s, h) => s + h.weight, 0) * 100;
  const palette = [
    "oklch(0.7 0.13 250)",
    "oklch(0.7 0.14 30)",
    "oklch(0.74 0.12 100)",
    "oklch(0.7 0.12 320)",
    "oklch(0.72 0.13 200)",
  ];

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          marginBottom: 8,
        }}
      >
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: ".08em",
            textTransform: "uppercase",
            color: theme.palette.text.secondary,
          }}
        >
          Top 5 holdings
        </span>
        <span
          style={{
            fontFamily: "ui-monospace",
            fontSize: 13,
            fontWeight: 600,
            color: theme.palette.text.primary,
          }}
        >
          {topPct.toFixed(1)}% of portfolio
        </span>
      </div>
      <div
        style={{
          display: "flex",
          height: 16,
          borderRadius: 4,
          overflow: "hidden",
          background: theme.palette.mode === "dark" ? "#1f1f24" : "#f4f1ec",
          marginBottom: 12,
        }}
      >
        {sorted.map((h, i) => (
          <div
            key={h.ticker}
            style={{
              width: (h.weight / (topPct / 100)) * 100 + "%",
              background: palette[i],
              minWidth: 2,
            }}
          />
        ))}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "6px 18px",
          fontSize: 12,
        }}
      >
        {sorted.map((h, i) => (
          <div
            key={h.ticker}
            style={{ display: "flex", alignItems: "center", gap: 8 }}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: 2,
                background: palette[i],
                flexShrink: 0,
              }}
            />
            <span
              style={{ fontWeight: 600, color: theme.palette.text.primary }}
            >
              {h.ticker.toUpperCase()}
            </span>
            <span
              style={{
                flex: 1,
                color: theme.palette.text.secondary,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {h.name}
            </span>
            <span
              style={{
                fontFamily: "ui-monospace",
                fontVariantNumeric: "tabular-nums",
                color: theme.palette.text.secondary,
              }}
            >
              {(h.weight * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Drawdown chart ──────────────────────────────────────────────────────

function DrawdownChart({
  drawdown,
}: {
  drawdown: { dates: string[]; drawdown_pct: number[] };
}) {
  const theme = useTheme();
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(800);
  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([e]) => setW(e.contentRect.width));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  const height = 170;
  const dd = drawdown.drawdown_pct;
  if (!dd.length) return null;
  const minDD = Math.min(...dd);
  const padT = 12,
    padB = 22,
    padL = 32;
  const innerW = Math.max(0, w - padL - 8);
  const innerH = height - padT - padB;
  const xPos = (i: number) => padL + (i / (dd.length - 1)) * innerW;
  const yPos = (v: number) => padT + (-v / (-minDD || 1)) * innerH;
  const path = dd
    .map(
      (v, i) => (i ? "L" : "M") + xPos(i).toFixed(1) + " " + yPos(v).toFixed(1),
    )
    .join(" ");
  const area =
    path + ` L ${xPos(dd.length - 1)} ${padT} L ${xPos(0)} ${padT} Z`;
  const worstIdx = dd.indexOf(minDD);
  const dn = theme.palette.error.main;

  return (
    <div ref={ref} style={{ width: "100%" }}>
      <svg width={w} height={height} style={{ display: "block" }}>
        <defs>
          <linearGradient id="ddgrad" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={dn} stopOpacity="0" />
            <stop offset="100%" stopColor={dn} stopOpacity="0.35" />
          </linearGradient>
        </defs>
        {[0, -2, -4, -6].map((g) => (
          <g key={g}>
            <line
              x1={padL}
              x2={padL + innerW}
              y1={yPos(g)}
              y2={yPos(g)}
              stroke={theme.palette.divider}
              strokeWidth="0.5"
              strokeDasharray={g === 0 ? "" : "2 3"}
            />
            <text
              x={padL - 6}
              y={yPos(g) + 3}
              fontSize="10"
              fill={theme.palette.text.secondary}
              fontFamily="ui-monospace"
              textAnchor="end"
            >
              {g}%
            </text>
          </g>
        ))}
        <path d={area} fill="url(#ddgrad)" />
        <path d={path} stroke={dn} strokeWidth="1.5" fill="none" />
        {worstIdx >= 0 && (
          <>
            <circle
              cx={xPos(worstIdx)}
              cy={yPos(minDD)}
              r="4"
              fill={theme.palette.background.paper}
              stroke={dn}
              strokeWidth="1.75"
            />
            <text
              x={xPos(worstIdx)}
              y={yPos(minDD) + 16}
              fontSize="10.5"
              fontWeight="600"
              fontFamily="ui-monospace"
              fill={dn}
              textAnchor="middle"
            >
              worst {minDD.toFixed(1)}%
            </text>
          </>
        )}
      </svg>
    </div>
  );
}

// ─── Correlation matrix ───────────────────────────────────────────────────

function CorrelationMatrix({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme();
  const top = useMemo(
    () =>
      [...assets]
        .sort((a, b) => (Number(b.value) || 0) - (Number(a.value) || 0))
        .slice(0, 10),
    [assets],
  );

  const corr = useMemo(() => {
    const n = top.length;
    const m = Array.from({ length: n }, () => Array(n).fill(0));
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i === j) {
          m[i][j] = 1;
          continue;
        }
        const a = top[i].price_series?.slice(-14) ?? [];
        const b = top[j].price_series?.slice(-14) ?? [];
        if (a.length < 2 || b.length < 2) {
          m[i][j] = 0;
          continue;
        }
        const len = Math.min(a.length, b.length);
        const ma = a.slice(0, len).reduce((s, v) => s + v, 0) / len;
        const mb = b.slice(0, len).reduce((s, v) => s + v, 0) / len;
        let num = 0,
          da = 0,
          db = 0;
        for (let k = 0; k < len; k++) {
          num += (a[k] - ma) * (b[k] - mb);
          da += (a[k] - ma) ** 2;
          db += (b[k] - mb) ** 2;
        }
        m[i][j] = num / (Math.sqrt(da * db) || 1);
      }
    }
    return m;
  }, [top]);

  const colour = (v: number) => {
    const intensity = Math.min(1, Math.abs(v));
    if (v >= 0)
      return `oklch(${0.97 - intensity * 0.3} ${0.04 + intensity * 0.12} 250)`;
    return `oklch(${0.97 - intensity * 0.3} ${0.04 + intensity * 0.12} 30)`;
  };
  const cell = 38;

  return (
    <div style={{ overflowX: "auto" }}>
      <div
        style={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: `52px repeat(${top.length}, ${cell}px)`,
          fontFamily: "ui-monospace",
          fontSize: 10.5,
        }}
      >
        <div />
        {top.map((h) => (
          <div
            key={h.ticker}
            style={{
              writingMode: "vertical-rl",
              transform: "rotate(180deg)",
              color: theme.palette.text.secondary,
              fontSize: 10,
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-end",
              padding: "4px 0",
            }}
          >
            {h.ticker.toUpperCase().slice(0, 5)}
          </div>
        ))}
        {top.map((h, i) => (
          <div key={h.ticker} style={{ display: "contents" }}>
            <div
              style={{
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: 10.5,
                display: "flex",
                alignItems: "center",
              }}
            >
              {h.ticker.toUpperCase().slice(0, 5)}
            </div>
            {top.map((_, j) => {
              const v = corr[i][j];
              return (
                <div
                  key={j}
                  title={`${top[i].ticker} ↔ ${top[j].ticker}: ${v.toFixed(2)}`}
                  style={{
                    width: cell,
                    height: cell,
                    background: colour(v),
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 10,
                    fontWeight: 600,
                    color:
                      Math.abs(v) > 0.55
                        ? theme.palette.text.primary
                        : theme.palette.text.secondary,
                    borderRadius: 3,
                    border:
                      i === j
                        ? `1px solid ${theme.palette.text.secondary}`
                        : "none",
                  }}
                >
                  {v.toFixed(2)}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Stress test ─────────────────────────────────────────────────────────

const SCENARIOS = [
  { name: "Market −10%", desc: "Broad equity selloff", impact: -7.4 },
  { name: "Tech selloff", desc: "Nasdaq −15%, others flat", impact: -9.1 },
  { name: "Rate hike +1%", desc: "Bonds, growth hit", impact: -3.2 },
  { name: "USD +5%", desc: "EUR strengthens", impact: -2.4 },
  { name: "Energy spike", desc: "Oil +25%", impact: 1.8 },
  { name: "Inflation +2%", desc: "Persistent CPI", impact: -4.6 },
];

function StressTest({ portfolioValue }: { portfolioValue: number }) {
  const theme = useTheme();
  const max = Math.max(...SCENARIOS.map((s) => Math.abs(s.impact)));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {SCENARIOS.map((s) => {
        const eur = (portfolioValue * s.impact) / 100;
        const w = (Math.abs(s.impact) / max) * 50;
        return (
          <div key={s.name}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                marginBottom: 4,
              }}
            >
              <div>
                <span
                  style={{
                    fontSize: 12.5,
                    fontWeight: 600,
                    color: theme.palette.text.primary,
                  }}
                >
                  {s.name}
                </span>
                <span
                  style={{
                    fontSize: 11,
                    color: theme.palette.text.secondary,
                    marginLeft: 8,
                  }}
                >
                  {s.desc}
                </span>
              </div>
              <div
                style={{
                  fontFamily: "ui-monospace",
                  fontSize: 12,
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                <span
                  style={{
                    fontWeight: 600,
                    color:
                      s.impact >= 0
                        ? theme.palette.success.main
                        : theme.palette.error.main,
                  }}
                >
                  {fmtPct(s.impact, 1)}
                </span>
                <span
                  style={{ color: theme.palette.text.secondary, marginLeft: 8 }}
                >
                  {eur >= 0 ? "+" : ""}
                  {fmtEUR(eur, 0)}
                </span>
              </div>
            </div>
            <div
              style={{
                position: "relative",
                height: 10,
                background:
                  theme.palette.mode === "dark" ? "#1f1f24" : "#f4f1ec",
                borderRadius: 3,
              }}
            >
              <div
                style={{
                  position: "absolute",
                  left: "50%",
                  top: 0,
                  bottom: 0,
                  width: 1,
                  background: theme.palette.text.secondary,
                  opacity: 0.4,
                }}
              />
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  bottom: 0,
                  left: s.impact >= 0 ? "50%" : 50 - w + "%",
                  width: w + "%",
                  background:
                    s.impact >= 0
                      ? theme.palette.success.main
                      : theme.palette.error.main,
                  borderRadius: 3,
                  opacity: 0.8,
                }}
              />
            </div>
          </div>
        );
      })}
      <div
        style={{
          marginTop: 6,
          padding: "10px 0 0",
          borderTop: `1px dashed ${theme.palette.divider}`,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11,
          color: theme.palette.text.secondary,
          fontFamily: "ui-monospace",
        }}
      >
        <span>Worst case</span>
        <span style={{ color: theme.palette.error.main, fontWeight: 600 }}>
          {fmtEUR(
            (portfolioValue * Math.min(...SCENARIOS.map((s) => s.impact))) /
              100,
            0,
          )}
        </span>
      </div>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────

function card(theme: Theme) {
  return {
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: 14,
    background: theme.palette.background.paper,
    padding: "18px 22px",
  };
}

export default function RiskTab() {
  const { summary } = usePortfolioContext();
  const theme = useTheme();

  if (!summary) return null;
  const { kpi, asset_table, portfolio_drawdown } = summary;

  return (
    <div style={{ padding: "32px 32px 40px", overflow: "auto" }}>
      <div style={{ marginBottom: 22 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: ".1em",
            textTransform: "uppercase",
            color: theme.palette.text.secondary,
          }}
        >
          Risk
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
          How much could I lose, and from what?
        </h2>
      </div>

      {/* Row 1: Concentration + Top-5 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 20,
          marginBottom: 20,
        }}
      >
        <div style={card(theme)}>
          <ConcentrationGauge assets={asset_table.rows} />
        </div>
        <div style={card(theme)}>
          <TopFiveBar assets={asset_table.rows} />
        </div>
      </div>

      {/* Row 2: Drawdown */}
      <div style={{ ...card(theme), marginBottom: 20 }}>
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
              Drawdown
            </div>
            <div
              style={{
                fontSize: 11,
                color: theme.palette.text.secondary,
                marginTop: 2,
              }}
            >
              Decline from running peak · last 6 months
            </div>
          </div>
        </div>
        <DrawdownChart drawdown={portfolio_drawdown} />
      </div>

      {/* Row 3: Correlation + Stress */}
      <div
        style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 20 }}
      >
        <div style={card(theme)}>
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
                Correlation matrix
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: theme.palette.text.secondary,
                  marginTop: 2,
                }}
              >
                Top 10 by value · price series · &gt; 0.6 means hidden
                concentration
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
              <span>−1</span>
              <span
                style={{
                  width: 70,
                  height: 10,
                  borderRadius: 2,
                  background:
                    "linear-gradient(90deg, oklch(0.72 0.14 30), oklch(0.97 0 0), oklch(0.72 0.14 250))",
                }}
              />
              <span>+1</span>
            </div>
          </div>
          <CorrelationMatrix assets={asset_table.rows} />
        </div>
        <div style={card(theme)}>
          <div style={{ marginBottom: 14 }}>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              Stress test
            </div>
            <div
              style={{
                fontSize: 11,
                color: theme.palette.text.secondary,
                marginTop: 2,
              }}
            >
              Simulated portfolio impact under shocks
            </div>
          </div>
          <StressTest portfolioValue={kpi.value} />
        </div>
      </div>
    </div>
  );
}
