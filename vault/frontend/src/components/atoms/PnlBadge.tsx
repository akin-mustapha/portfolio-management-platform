import { Chip, useTheme } from "@mui/material";

interface PnlBadgeProps {
  value: number;
  formatAs?: "currency" | "percent";
  symbol?: string;
}

export default function PnlBadge({
  value,
  formatAs = "currency",
  symbol = "",
}: PnlBadgeProps) {
  const theme = useTheme();
  const positive = value >= 0;
  const color = positive
    ? theme.palette.success.main
    : theme.palette.error.main;

  const label =
    formatAs === "percent"
      ? `${positive ? "+" : ""}${value.toFixed(2)}%`
      : `${positive ? "+" : ""}${symbol}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <Chip
      label={label}
      size="small"
      sx={{
        backgroundColor: color + "22",
        color,
        fontWeight: 600,
        fontSize: 11,
        height: 20,
      }}
    />
  );
}
