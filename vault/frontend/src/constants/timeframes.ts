export type TimeframeOption = "1d" | "1w" | "1m" | "3m" | "6m" | "1y" | "all";

export const TIMEFRAME_OPTIONS: { value: TimeframeOption; label: string }[] = [
  { value: "1d", label: "1D" },
  { value: "1w", label: "1W" },
  { value: "1m", label: "1M" },
  { value: "3m", label: "3M" },
  { value: "6m", label: "6M" },
  { value: "1y", label: "1Y" },
  { value: "all", label: "All" },
];
