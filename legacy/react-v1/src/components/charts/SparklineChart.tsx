import { useId, useMemo } from "react";
import { useTheme } from "@mui/material";
import { AreaChart, Area, ResponsiveContainer, ReferenceLine } from "recharts";

interface SparklineChartProps {
  values?: (number | null)[];
  /** 'positive' | 'negative' | 'neutral' drives line color; defaults to neutral */
  sentiment?: "positive" | "negative" | "neutral";
  height?: number;
  /** Render a subtle gradient fill under the line */
  fill?: boolean;
}

export default function SparklineChart({
  values,
  sentiment = "neutral",
  height = 36,
  fill = false,
}: SparklineChartProps) {
  const theme = useTheme();
  const rawId = useId();
  const gradId = useMemo(() => rawId.replace(/[^a-zA-Z0-9]/g, ""), [rawId]);
  const data = useMemo(
    () => (values ?? []).map((v, i) => ({ i, v })),
    [values],
  );

  if (!values?.length) return null;

  const color =
    sentiment === "positive"
      ? theme.palette.success.main
      : sentiment === "negative"
        ? theme.palette.error.main
        : theme.palette.text.secondary;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
        {fill && (
          <defs>
            <linearGradient id={`spark-${gradId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.22} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
        )}
        <ReferenceLine
          y={0}
          stroke={theme.palette.divider}
          strokeDasharray="2 2"
        />
        <Area
          type="monotone"
          dataKey="v"
          stroke={color}
          strokeWidth={2}
          fill={fill ? `url(#spark-${gradId})` : "transparent"}
          dot={false}
          activeDot={false}
          isAnimationActive={true}
          animationDuration={500}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
