import { useTheme } from "@mui/material";

export function useTooltipStyle() {
  const theme = useTheme();
  return {
    backgroundColor: theme.palette.background.paper,
    borderColor: theme.palette.divider,
    fontSize: 11,
  };
}

export function fmtNum(v: unknown, decimals = 2): string {
  if (v == null) return "—";
  return Number(v).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}
