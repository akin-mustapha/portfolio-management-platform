import { useTheme } from "@mui/material";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

interface VarItem {
  ticker: string;
  var_95_1d: number;
  name: string;
}

interface VarByPositionChartProps {
  varData?: VarItem[];
}

export default function VarByPositionChart({
  varData,
}: VarByPositionChartProps) {
  const theme = useTheme();
  if (!varData?.length) return null;

  function CustomTooltip({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: unknown[];
  }) {
    if (!active || !payload?.length) return null;
    const d = (payload as Array<{ payload: VarItem }>)[0].payload;
    return (
      <div
        style={{
          background: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          padding: "6px 10px",
          fontSize: 11,
          borderRadius: 4,
        }}
      >
        <div style={{ fontWeight: 600 }}>{d.ticker}</div>
        <div
          style={{
            color: theme.palette.text.secondary,
            fontSize: 10,
            marginBottom: 2,
          }}
        >
          {d.name}
        </div>
        <div>VaR 95% 1d: {d.var_95_1d.toFixed(4)}</div>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart
        data={varData}
        margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="ticker" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={55} />
        <Tooltip
          content={<CustomTooltip />}
          cursor={{ fill: theme.palette.action.hover }}
        />
        <Bar dataKey="var_95_1d" radius={[3, 3, 0, 0]}>
          {varData.map((_, i) => (
            <Cell
              key={i}
              fill={theme.palette.error.main}
              opacity={0.9 - i * 0.06}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
