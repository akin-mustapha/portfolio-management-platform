// Sector allocation donut with legend
import { useTheme } from "@mui/material";

export interface SectorSlice {
  sector: string;
  value: number;
  weight: number;
}

const PALETTE = [
  "oklch(0.7 0.13 250)",
  "oklch(0.72 0.13 30)",
  "oklch(0.74 0.12 100)",
  "oklch(0.7 0.12 320)",
  "oklch(0.72 0.13 200)",
  "oklch(0.7 0.12 60)",
  "oklch(0.72 0.1 350)",
  "oklch(0.72 0.1 280)",
  "oklch(0.74 0.07 160)",
];

interface DonutProps {
  sectors: SectorSlice[];
  holdingsCount: number;
  size?: number;
  thick?: number;
}

export default function DonutChart({
  sectors,
  holdingsCount,
  size = 160,
  thick = 22,
}: DonutProps) {
  const theme = useTheme();
  const r = size / 2 - thick / 2;
  const cx = size / 2,
    cy = size / 2;
  const C = 2 * Math.PI * r;
  let off = 0;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
      <svg width={size} height={size} style={{ flexShrink: 0 }}>
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={theme.palette.mode === "dark" ? "#1f1f24" : "#f4f1ec"}
          strokeWidth={thick}
        />
        {sectors.map((s, i) => {
          const len = C * s.weight;
          const dash = `${len} ${C - len}`;
          const el = (
            <circle
              key={s.sector}
              cx={cx}
              cy={cy}
              r={r}
              fill="none"
              stroke={PALETTE[i % PALETTE.length]}
              strokeWidth={thick}
              strokeDasharray={dash}
              strokeDashoffset={-off}
              transform={`rotate(-90 ${cx} ${cy})`}
            />
          );
          off += len;
          return el;
        })}
        <text
          x={cx}
          y={cy - 4}
          textAnchor="middle"
          fontSize="10.5"
          fill={theme.palette.text.secondary}
          letterSpacing="0.06em"
        >
          SECTORS
        </text>
        <text
          x={cx}
          y={cy + 14}
          textAnchor="middle"
          fontSize="20"
          fontWeight="600"
          fill={theme.palette.text.primary}
          fontFamily="ui-monospace"
        >
          {holdingsCount}
        </text>
      </svg>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "6px 14px",
          fontSize: 11.5,
          flex: 1,
        }}
      >
        {sectors.map((s, i) => (
          <div
            key={s.sector}
            style={{ display: "flex", alignItems: "center", gap: 6 }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: 2,
                background: PALETTE[i % PALETTE.length],
                flexShrink: 0,
              }}
            />
            <span style={{ flex: 1, color: theme.palette.text.primary }}>
              {s.sector}
            </span>
            <span
              style={{
                color: theme.palette.text.secondary,
                fontFamily: "ui-monospace",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {(s.weight * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
