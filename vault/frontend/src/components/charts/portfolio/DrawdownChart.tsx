import { useMemo } from "react";
import { useTheme } from "@mui/material";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { useTooltipStyle } from "../../../utils/chartUtils";

interface DrawdownChartProps {
  drawdown?: { dates: string[]; drawdown_pct: number[] };
}

export default function DrawdownChart({ drawdown }: DrawdownChartProps) {
  const theme = useTheme();
  const tooltipStyle = useTooltipStyle();
  const data = useMemo(
    () =>
      (drawdown?.dates ?? []).map((d, i) => ({
        date: d,
        drawdown: drawdown?.drawdown_pct[i],
      })),
    [drawdown?.dates, drawdown?.drawdown_pct],
  );
  if (!drawdown?.dates?.length) return null;
  const errorColor = theme.palette.error.main;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={errorColor} stopOpacity={0.55} />
            <stop offset="60%" stopColor={errorColor} stopOpacity={0.18} />
            <stop offset="100%" stopColor={errorColor} stopOpacity={0} />
          </linearGradient>
          <filter id="ddGlow" x="-10%" y="-10%" width="120%" height="130%">
            <feGaussianBlur stdDeviation="2.4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={theme.palette.divider}
          strokeOpacity={0.35}
          vertical={false}
        />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={{ stroke: theme.palette.divider }}
        />
        <YAxis
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          width={50}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, "Drawdown"]}
        />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Area
          type="monotone"
          dataKey="drawdown"
          stroke={errorColor}
          strokeWidth={2.5}
          fill="url(#ddGrad)"
          dot={false}
          activeDot={{ r: 4, strokeWidth: 0, fill: errorColor }}
          style={{ filter: "url(#ddGlow)" }}
          isAnimationActive
          animationDuration={700}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
