import { Box, Typography } from "@mui/material";
import KpiCard from "../atoms/KpiCard";
import type { MetricKey } from "../../constants/metricDefinitions";

export interface KpiGroupItem {
  label: string;
  value?: number | string | null;
  prefix?: string;
  suffix?: string;
  colorCode?: "positive" | "negative" | "neutral";
  metricKey?: MetricKey;
  sparkline?: (number | null)[];
}

interface KpiGroupProps {
  label: string;
  cards: KpiGroupItem[];
  loading?: boolean;
  /** Force single-row horizontal scroll (default) vs wrap */
  overflow?: "scroll" | "wrap";
  dimmed?: boolean;
}

export default function KpiGroup({
  label,
  cards,
  loading = false,
  overflow = "scroll",
  dimmed = true,
}: KpiGroupProps) {
  const anyHasSparkline = cards.some(
    (c) => c.sparkline && c.sparkline.length > 0,
  );
  return (
    <Box
      sx={(theme) => ({
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 3,
        px: 2,
        py: 1.75,
        bgcolor: "background.paper",
        boxShadow: theme.custom.shadowCard,
        display: "flex",
        flexDirection: "column",
        gap: 1.25,
        flex: "1 1 auto",
        minWidth: 0,
        opacity: dimmed ? 0.82 : 1,
        transition: "box-shadow 180ms ease, opacity 180ms ease",
        "&:hover": { boxShadow: theme.custom.shadowCardHover, opacity: 1 },
      })}
    >
      <Typography
        variant="caption"
        color="text.disabled"
        sx={{
          fontWeight: 600,
          letterSpacing: 1,
          textTransform: "uppercase",
          fontSize: 10,
        }}
        component="div"
      >
        {label}
      </Typography>
      <Box
        sx={{
          display: "flex",
          alignItems: "stretch",
          flex: 1,
          ...(overflow === "scroll"
            ? {
                overflowX: "auto",
                overflowY: "hidden",
                scrollbarWidth: "thin",
                mx: -0.5,
                px: 0.5,
                "&::-webkit-scrollbar": { height: 6 },
                "&::-webkit-scrollbar-thumb": {
                  backgroundColor: "divider",
                  borderRadius: 3,
                },
                "&::-webkit-scrollbar-track": { background: "transparent" },
              }
            : { flexWrap: "wrap" }),
        }}
      >
        {cards.map((card, idx) => (
          <Box
            key={card.label}
            sx={{
              flex: overflow === "scroll" ? "0 0 auto" : "1 1 0",
              minWidth: 120,
              pl: idx === 0 ? 0 : 1.25,
              pr: idx === cards.length - 1 ? 0 : 1.25,
              borderLeft: idx === 0 ? "none" : "1px solid",
              borderColor: "divider",
            }}
          >
            <KpiCard
              label={card.label}
              value={card.value}
              prefix={card.prefix}
              suffix={card.suffix}
              colorCode={card.colorCode ?? "neutral"}
              metricKey={card.metricKey}
              sparkline={card.sparkline}
              loading={loading}
              compact
              reserveSparklineSlot={anyHasSparkline}
            />
          </Box>
        ))}
      </Box>
    </Box>
  );
}
