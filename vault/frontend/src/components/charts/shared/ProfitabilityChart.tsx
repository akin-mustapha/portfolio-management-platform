import { useTheme } from "@mui/material";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTooltipStyle } from "../../../utils/chartUtils";
import type { ProfitabilityVM } from "../../../presenters/riskPresenter";

interface ProfitabilityChartProps {
  vm?: ProfitabilityVM;
}

export default function ProfitabilityChart({ vm }: ProfitabilityChartProps) {
  const theme = useTheme();
  const tooltipStyle = useTooltipStyle();
  if (!vm) return null;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={vm.data}
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
