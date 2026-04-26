// Winners / Losers card for today's movers
import { useState } from "react";
import { useTheme } from "@mui/material";
import type { Theme } from "@mui/material";
import {
  TickerGlyph,
  fmtPct,
} from "../../../components/charts/design/DesignPrimitives";
import type { DailyMoverItem } from "../../../presenters/portfolioPresenter";

interface MoversCardProps {
  title: string;
  items: DailyMoverItem[];
}

export default function MoversCard({ title, items }: MoversCardProps) {
  const theme = useTheme();
  return (
    <div
      style={{
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 12,
        background: theme.palette.background.paper,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: "10px 14px",
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: ".06em",
          textTransform: "uppercase",
          color: theme.palette.text.secondary,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        {title}
      </div>
      {items.map((h) => (
        <MoverRow key={h.ticker} item={h} />
      ))}
    </div>
  );
}

function MoverRow({ item }: { item: DailyMoverItem }) {
  const theme = useTheme();
  const [hover, setHover] = useState(false);
  const up = item.daily_value_return >= 0;
  const color = up ? theme.palette.success.main : theme.palette.error.main;
  const sector =
    ((item as unknown as Record<string, unknown>).sector as string) ?? "";
  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "8px 14px",
        fontSize: 12,
        borderBottom: `1px solid ${theme.palette.mode === "dark" ? "#1f1f24" : "#f4f1ec"}`,
        background: hover
          ? (theme as Theme & { custom: { bgRowHover: string } }).custom
              .bgRowHover
          : "transparent",
        transition: "background .12s",
        cursor: "default",
      }}
    >
      <TickerGlyph ticker={item.ticker} sector={sector} size={20} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, color: theme.palette.text.primary }}>
          {item.ticker.toUpperCase()}
        </div>
        <div
          style={{
            fontSize: 10.5,
            color: theme.palette.text.secondary,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {item.name}
        </div>
      </div>
      <span
        style={{
          fontFamily: "ui-monospace",
          fontVariantNumeric: "tabular-nums",
          fontWeight: 600,
          color,
          whiteSpace: "nowrap",
        }}
      >
        {fmtPct(item.daily_value_return, 2)}
      </span>
    </div>
  );
}
