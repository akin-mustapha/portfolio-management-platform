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
} from "recharts";
import { useTooltipStyle, fmtNum } from "../../utils/chartUtils";

interface AssetValueChartProps {
  series?: { dates: string[]; values: (number | null)[] };
  title?: string;
  color?: string;
}

export default function AssetValueChart({
  series,
  title,
  color,
}: AssetValueChartProps) {
  const theme = useTheme();
  const tooltipStyle = useTooltipStyle();
  const lineColor = color ?? theme.palette.primary.main;
  const data = useMemo(
    () =>
      (series?.dates ?? []).map((d, i) => ({
        date: d,
        value: series?.values[i],
      })),
    [series?.dates, series?.values],
  );
  if (!series?.dates?.length) return null;

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={`avGrad-${title}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={lineColor} stopOpacity={0.28} />
            <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={theme.palette.divider}
          strokeOpacity={0.5}
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
          width={60}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [fmtNum(v), title ?? "Value"]}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke={lineColor}
          fill={`url(#avGrad-${title})`}
          strokeWidth={2.25}
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
