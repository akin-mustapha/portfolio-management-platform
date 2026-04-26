import { useTheme } from "@mui/material";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTooltipStyle } from "../../utils/chartUtils";

interface ProfitabilityChartProps {
  assets?: Array<{ ticker: string; profit: number }>;
}

export default function ProfitabilityChart({
  assets,
}: ProfitabilityChartProps) {
  const theme = useTheme();
  const tooltipStyle = useTooltipStyle();
  if (!assets?.length) return null;

  const profitable = assets.filter((a) => (a.profit ?? 0) > 0).length;
  const unprofitable = assets.length - profitable;

  const data = [
    { name: "Profitable", value: profitable },
    { name: "Unprofitable", value: unprofitable },
  ];

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          cx="50%"
          cy="50%"
          outerRadius={75}
          innerRadius={35}
          paddingAngle={3}
        >
          <Cell fill={theme.palette.success.main} />
          <Cell fill={theme.palette.error.main} />
        </Pie>
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
