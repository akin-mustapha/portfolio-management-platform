// Risk vs Return bubble scatter — volatility (x), return (y), bubble size = weight
import { useState, useRef, useEffect } from "react";
import { useTheme } from "@mui/material";
import { fmtPct } from "./DesignPrimitives";

export interface ScatterPoint {
  ticker: string;
  name: string;
  vol: number;
  ret: number;
  beta: number;
  weight: number;
}

interface RiskReturnScatterProps {
  items: ScatterPoint[];
  height?: number;
  onPick?: (item: ScatterPoint) => void;
}

export default function RiskReturnScatter({
  items,
  height = 320,
  onPick,
}: RiskReturnScatterProps) {
  const theme = useTheme();
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(600);
  const [hov, setHov] = useState<string | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([e]) => setW(e.contentRect.width));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  const padL = 40,
    padR = 14,
    padT = 14,
    padB = 28;
  const innerW = w - padL - padR,
    innerH = height - padT - padB;
  const xMin = 0,
    xMax = 45;
  const yMin = -45,
    yMax = 45;
  const xToPx = (v: number) => padL + ((v - xMin) / (xMax - xMin)) * innerW;
  const yToPx = (v: number) => padT + (1 - (v - yMin) / (yMax - yMin)) * innerH;

  const up = theme.palette.success.main;
  const dn = theme.palette.error.main;
  const upBg =
    theme.palette.mode === "dark"
      ? "rgba(74,222,128,0.08)"
      : "rgba(22,163,74,0.06)";
  const dnBg =
    theme.palette.mode === "dark"
      ? "rgba(248,113,113,0.08)"
      : "rgba(220,38,38,0.06)";

  const hovItem = hov ? items.find((x) => x.ticker === hov) : null;

  return (
    <div ref={ref}>
      <svg width={w} height={height} style={{ display: "block" }}>
        {/* quadrant backgrounds */}
        <rect
          x={padL}
          y={padT}
          width={innerW}
          height={yToPx(0) - padT}
          fill={upBg}
        />
        <rect
          x={padL}
          y={yToPx(0)}
          width={innerW}
          height={padT + innerH - yToPx(0)}
          fill={dnBg}
        />

        {/* y gridlines */}
        {[-30, -15, 0, 15, 30].map((g) => (
          <g key={g}>
            <line
              x1={padL}
              x2={padL + innerW}
              y1={yToPx(g)}
              y2={yToPx(g)}
              stroke={theme.palette.divider}
              strokeWidth={g === 0 ? 1 : 0.5}
              strokeDasharray={g === 0 ? "" : "2 3"}
            />
            <text
              x={padL - 6}
              y={yToPx(g) + 3}
              textAnchor="end"
              fontSize="10"
              fill={theme.palette.text.secondary}
              fontFamily="ui-monospace"
            >
              {g}%
            </text>
          </g>
        ))}
        {/* x gridlines */}
        {[10, 20, 30, 40].map((g) => (
          <g key={g}>
            <line
              x1={xToPx(g)}
              x2={xToPx(g)}
              y1={padT}
              y2={padT + innerH}
              stroke={theme.palette.divider}
              strokeWidth={0.5}
              strokeDasharray="2 3"
            />
            <text
              x={xToPx(g)}
              y={height - 10}
              textAnchor="middle"
              fontSize="10"
              fill={theme.palette.text.secondary}
              fontFamily="ui-monospace"
            >
              {g}%
            </text>
          </g>
        ))}

        <text
          x={padL}
          y={height - 2}
          fontSize="9.5"
          fill={theme.palette.text.secondary}
          fontFamily="ui-monospace"
          letterSpacing="0.04em"
        >
          VOLATILITY →
        </text>
        <text
          x={4}
          y={padT + 8}
          fontSize="9.5"
          fill={theme.palette.text.secondary}
          fontFamily="ui-monospace"
          letterSpacing="0.04em"
        >
          ↑ RETURN
        </text>

        {/* bubbles */}
        {items.map((h) => {
          const cx = xToPx(Math.min(h.vol, xMax - 1));
          const cy = yToPx(Math.max(yMin + 1, Math.min(yMax - 1, h.ret)));
          const r = Math.max(5, Math.min(26, Math.sqrt(h.weight * 600) + 4));
          const isHov = hov === h.ticker;
          const fill = h.ret >= 0 ? up : dn;
          return (
            <g
              key={h.ticker}
              onMouseEnter={() => setHov(h.ticker)}
              onMouseLeave={() => setHov(null)}
              onClick={() => onPick?.(h)}
              style={{ cursor: "pointer" }}
            >
              <circle
                cx={cx}
                cy={cy}
                r={r}
                fill={fill}
                fillOpacity={0.18}
                stroke={fill}
                strokeWidth={isHov ? 2 : 1}
              />
              {(r > 9 || isHov) && (
                <text
                  x={cx}
                  y={cy + 3.5}
                  textAnchor="middle"
                  fontSize="10"
                  fontWeight="600"
                  fill={theme.palette.text.primary}
                  pointerEvents="none"
                >
                  {h.ticker.toUpperCase().slice(0, 4)}
                </text>
              )}
            </g>
          );
        })}

        {/* tooltip */}
        {hovItem &&
          (() => {
            const cx = xToPx(Math.min(hovItem.vol, xMax - 1));
            const cy = yToPx(
              Math.max(yMin + 1, Math.min(yMax - 1, hovItem.ret)),
            );
            const tipX = Math.min(cx + 14, w - 160);
            const tipY = Math.max(padT + 4, cy - 32);
            return (
              <g pointerEvents="none">
                <rect
                  x={tipX}
                  y={tipY}
                  rx={6}
                  width={155}
                  height={58}
                  fill={theme.palette.background.paper}
                  stroke={theme.palette.divider}
                />
                <text
                  x={tipX + 8}
                  y={tipY + 18}
                  fontSize="11"
                  fontWeight="600"
                  fill={theme.palette.text.primary}
                >
                  {hovItem.ticker.toUpperCase()} · {hovItem.name.slice(0, 14)}
                </text>
                <text
                  x={tipX + 8}
                  y={tipY + 32}
                  fontSize="10.5"
                  fill={theme.palette.text.secondary}
                  fontFamily="ui-monospace"
                >
                  vol {hovItem.vol.toFixed(1)}% · β {hovItem.beta.toFixed(2)}
                </text>
                <text
                  x={tipX + 8}
                  y={tipY + 47}
                  fontSize="10.5"
                  fontFamily="ui-monospace"
                  fontWeight="600"
                  fill={hovItem.ret >= 0 ? up : dn}
                >
                  {fmtPct(hovItem.ret, 1)} return
                </text>
              </g>
            );
          })()}
      </svg>
    </div>
  );
}
