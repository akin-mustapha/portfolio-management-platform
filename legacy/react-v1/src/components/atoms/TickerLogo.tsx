import { Avatar } from "@mui/material";
import { useState } from "react";

interface TickerLogoProps {
  ticker: string;
  size?: number;
}

// Trading212 appends a lowercase exchange suffix to tickers (e.g. ASMLa, CHVd, IWDPl).
// FMP uses clean tickers, so strip any trailing single lowercase letter.
function cleanTicker(ticker: string): string {
  return ticker.replace(/[a-z]$/, "");
}

// Module-level cache so error state survives DataGrid row virtualization (unmount/remount).
const erroredTickers = new Set<string>();

export default function TickerLogo({ ticker, size = 24 }: TickerLogoProps) {
  const [errored, setErrored] = useState(() => erroredTickers.has(ticker));
  const clean = cleanTicker(ticker);

  function handleError() {
    erroredTickers.add(ticker);
    setErrored(true);
  }

  return (
    <Avatar
      src={
        errored
          ? undefined
          : `https://financialmodelingprep.com/image-stock/${clean}.png`
      }
      alt={ticker}
      slotProps={{ img: { onError: handleError } }}
      sx={{
        width: size,
        height: size,
        fontSize: size * 0.45,
        fontWeight: 600,
        bgcolor: "action.selected",
        color: "text.primary",
        border: "1px solid",
        borderColor: "divider",
        flexShrink: 0,
      }}
    >
      {ticker[0]}
    </Avatar>
  );
}
