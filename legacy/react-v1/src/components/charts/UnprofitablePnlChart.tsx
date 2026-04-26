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
import { useTooltipStyle, fmtNum } from "../../utils/chartUtils";

interface UnprofitablePnlChartProps {
  /** losers_pnl from presenter: { [date]: summed_profit } */
  losersData?: Record<string, number>;
}

export default function UnprofitablePnlChart({
  losersData,
}: UnprofitablePnlChartProps) {
  const theme = useTheme();
  const tooltipStyle = useTooltipStyle();

  if (!losersData || !Object.keys(losersData).length) return null;

  const data = Object.entries(losersData)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, value]) => ({ date, value }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="lossPnlGrad" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="5%"
              stopColor={theme.palette.error.main}
              stopOpacity={0}
            />
            <stop
              offset="95%"
              stopColor={theme.palette.error.main}
              stopOpacity={0.35}
            />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [fmtNum(v), "Unprofitable P&L"]}
        />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Area
          type="monotone"
          dataKey="value"
          stroke={theme.palette.error.main}
          fill="url(#lossPnlGrad)"
          strokeWidth={1.5}
          dot={false}
          baseValue={0}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
