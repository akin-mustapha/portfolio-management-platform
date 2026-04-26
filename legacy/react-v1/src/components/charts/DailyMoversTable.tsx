import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  useTheme,
} from "@mui/material";

interface DailyMoversTableProps {
  movers?: Array<{ ticker: string; daily_value_return: number; name: string }>;
}

export default function DailyMoversTable({ movers }: DailyMoversTableProps) {
  const theme = useTheme();
  if (!movers?.length) return null;

  return (
    <Box sx={{ height: 300, overflowY: "auto", overflowX: "hidden" }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontSize: 11, fontWeight: 700 }}>Ticker</TableCell>
            <TableCell sx={{ fontSize: 11, fontWeight: 700 }}>Name</TableCell>
            <TableCell align="right" sx={{ fontSize: 11, fontWeight: 700 }}>
              Daily Return
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {movers.map((m) => (
            <TableRow key={m.ticker} hover>
              <TableCell sx={{ fontSize: 11 }}>{m.ticker}</TableCell>
              <TableCell
                sx={{
                  fontSize: 11,
                  color: theme.palette.text.secondary,
                  maxWidth: 180,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={m.name}
              >
                {m.name}
              </TableCell>
              <TableCell
                align="right"
                sx={{
                  fontSize: 11,
                  fontWeight: 600,
                  color:
                    m.daily_value_return >= 0
                      ? theme.palette.success.main
                      : theme.palette.error.main,
                }}
              >
                {m.daily_value_return >= 0 ? "+" : ""}
                {m.daily_value_return.toFixed(2)}%
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
