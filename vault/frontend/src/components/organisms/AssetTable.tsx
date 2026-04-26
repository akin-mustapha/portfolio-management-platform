import { useMemo } from "react";
import {
  DataGrid,
  type GridColDef,
  type GridRenderCellParams,
} from "@mui/x-data-grid";
import {
  Autocomplete,
  Box,
  Chip,
  IconButton,
  TextField,
  Tooltip,
  Typography,
  useTheme,
  type Theme,
} from "@mui/material";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { useAppStore } from "../../store/useAppStore";
import { SparklineChart } from "../charts/shared";
import MetricInfo from "../atoms/MetricInfo";
import TickerLogo from "../atoms/TickerLogo";
import {
  fmtNum as numFmt,
  fmtPct as pctFmt,
  sparklineSentiment,
} from "../../presenters/assetPresenter";

interface AssetTableProps {
  rows: Record<string, unknown>[];
  loading?: boolean;
  availableTags?: string[];
  onOpenDetails?: (ticker: string) => void;
}

function getRowClassName(params: {
  indexRelativeToCurrentPage: number;
  row: Record<string, unknown>;
}) {
  const parity =
    params.indexRelativeToCurrentPage % 2 === 0 ? "row-even" : "row-odd";
  const profit = Number(params.row.profit);
  const sentiment =
    !Number.isFinite(profit) || profit === 0
      ? ""
      : profit > 0
        ? "row-positive"
        : "row-negative";
  return `${parity} ${sentiment}`;
}

function headerWithInfo(
  label: string,
  metricKey: Parameters<typeof MetricInfo>[0]["metricKey"],
) {
  return () => (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
      <span style={{ fontSize: 11, fontWeight: 700 }}>{label}</span>
      <MetricInfo metricKey={metricKey} />
    </Box>
  );
}

const NUM: Pick<GridColDef, "align" | "headerAlign"> = {
  align: "right",
  headerAlign: "right",
};

function buildColumns(
  theme: Theme,
  onOpenDetails?: (ticker: string) => void,
): GridColDef[] {
  return [
    {
      field: "price_series",
      headerName: "30D",
      width: 100,
      headerAlign: "center",
      align: "center",
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams) => {
        const values = params.value as (number | null)[] | undefined;
        if (!values?.length) return null;
        return (
          <SparklineChart
            values={values}
            sentiment={sparklineSentiment(values)}
            height={32}
          />
        );
      },
    },
    {
      field: "ticker",
      headerName: "Ticker",
      width: 110,
      pinnable: true,
      renderCell: (params: GridRenderCellParams) => (
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
          <TickerLogo ticker={params.value as string} size={22} />
          <span style={{ fontWeight: 600, fontSize: 12.5 }}>
            {params.value as string}
          </span>
        </Box>
      ),
    },
    {
      field: "name",
      headerName: "Name",
      width: 220,
      renderCell: (params: GridRenderCellParams) => (
        <span style={{ fontWeight: 500, color: theme.palette.text.primary }}>
          {params.value as string}
        </span>
      ),
    },
    {
      field: "__details",
      headerName: "",
      width: 40,
      sortable: false,
      filterable: false,
      disableColumnMenu: true,
      resizable: false,
      align: "center",
      headerAlign: "center",
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title="Open details">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onOpenDetails?.(params.row.ticker as string);
            }}
            sx={{
              opacity: 0.55,
              transition: "opacity 150ms ease, color 150ms ease",
              "&:hover": { opacity: 1, color: "primary.main" },
            }}
          >
            <OpenInNewIcon sx={{ fontSize: 14 }} />
          </IconButton>
        </Tooltip>
      ),
    },
    {
      field: "price",
      headerName: "Price",
      width: 90,
      valueFormatter: (v) => numFmt(v),
      ...NUM,
    },
    {
      field: "avg_price",
      headerName: "Avg Price",
      width: 90,
      valueFormatter: (v) => numFmt(v),
      renderHeader: headerWithInfo("Avg Price", "avg_price"),
      ...NUM,
    },
    {
      field: "price_vs_avg_pct",
      headerName: "vs Avg %",
      width: 90,
      valueGetter: (_value: unknown, row: Record<string, unknown>) => {
        const price = Number(row.price);
        const avg = Number(row.avg_price);
        if (!avg) return null;
        return ((price - avg) / avg) * 100;
      },
      valueFormatter: pctFmt,
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      ...NUM,
    },
    {
      field: "value",
      headerName: "Value",
      width: 110,
      valueFormatter: (v) => numFmt(v),
      ...NUM,
    },
    {
      field: "cost",
      headerName: "Cost",
      width: 110,
      valueFormatter: (v) => numFmt(v),
      ...NUM,
    },
    {
      field: "profit",
      headerName: "P&L",
      width: 110,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("P&L", "profit"),
      ...NUM,
    },
    {
      field: "pnl_pct",
      headerName: "P&L %",
      width: 90,
      valueFormatter: pctFmt,
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("P&L %", "pnl_pct"),
      ...NUM,
    },
    {
      field: "weight_pct",
      headerName: "Weight %",
      width: 90,
      valueFormatter: pctFmt,
      renderHeader: headerWithInfo("Weight %", "weight_pct"),
      ...NUM,
    },
    {
      field: "daily_value_return",
      headerName: "Daily Return",
      width: 100,
      valueFormatter: (v) =>
        v != null ? `${(Number(v) * 100).toFixed(2)}%` : "—",
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("Daily Return", "daily_value_return"),
      ...NUM,
    },
    {
      field: "cumulative_value_return",
      headerName: "Cum. Return",
      width: 110,
      valueFormatter: pctFmt,
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("Cum. Return", "cumulative_value_return"),
      ...NUM,
    },
    {
      field: "trend",
      headerName: "Trend",
      width: 100,
      renderHeader: headerWithInfo("Trend", "trend"),
      align: "center",
      headerAlign: "center",
      renderCell: (params: GridRenderCellParams) => {
        const val = params.value as string;
        const isBullish = val === "Bullish";
        return (
          <Chip
            label={val}
            size="small"
            sx={{
              height: 20,
              fontSize: 10,
              fontWeight: 700,
              bgcolor: isBullish
                ? theme.palette.success.main
                : theme.palette.error.main,
              color: "#fff",
            }}
          />
        );
      },
    },
    {
      field: "dca_bias",
      headerName: "DCA Bias",
      width: 90,
      valueFormatter: (v) => numFmt(v, 4),
      cellClassName: (p) =>
        Number(p.value) < 1 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("DCA Bias", "dca_bias"),
      ...NUM,
    },
    {
      field: "volatility_30d",
      headerName: "Vol 30d",
      width: 90,
      valueFormatter: (v) => numFmt(v, 4),
      renderHeader: headerWithInfo("Vol 30d", "volatility_30d"),
      ...NUM,
    },
    {
      field: "volatility_50d",
      headerName: "Vol 50d",
      width: 90,
      valueFormatter: (v) => numFmt(v, 4),
      ...NUM,
    },
    {
      field: "var_95_1d",
      headerName: "VaR 95%",
      width: 90,
      valueFormatter: (v) => numFmt(v, 4),
      renderHeader: headerWithInfo("VaR 95%", "var_95_1d"),
      ...NUM,
    },
    {
      field: "beta_60d",
      headerName: "Beta 60d",
      width: 90,
      valueFormatter: (v) => numFmt(v, 3),
      cellClassName: (p) =>
        p.value != null
          ? Number(p.value) > 1
            ? "cell-negative"
            : "cell-positive"
          : "",
      ...NUM,
    },
    {
      field: "asset_sharpe_ratio_30d",
      headerName: "Sharpe",
      width: 80,
      valueFormatter: (v) => numFmt(v, 2),
      cellClassName: (p) =>
        p.value != null
          ? Number(p.value) >= 1
            ? "cell-positive"
            : "cell-negative"
          : "",
      ...NUM,
    },
    {
      field: "value_ma_30d",
      headerName: "MA 30d",
      width: 90,
      valueFormatter: (v) => numFmt(v),
      ...NUM,
    },
    {
      field: "value_ma_50d",
      headerName: "MA 50d",
      width: 90,
      valueFormatter: (v) => numFmt(v),
      ...NUM,
    },
    {
      field: "value_drawdown_pct_30d",
      headerName: "Drawdown 30d",
      width: 120,
      valueFormatter: pctFmt,
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("Drawdown 30d", "value_drawdown_pct_30d"),
      ...NUM,
    },
    {
      field: "recent_profit_high_30d",
      headerName: "P&L High 30d",
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      renderHeader: headerWithInfo("P&L High 30d", "recent_profit_high_30d"),
      ...NUM,
    },
    {
      field: "recent_profit_low_30d",
      headerName: "P&L Low 30d",
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) =>
        Number(p.value) >= 0 ? "cell-positive" : "cell-negative",
      ...NUM,
    },
    {
      field: "recent_value_high_30d",
      headerName: "Val High 30d",
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => {
        const high = Number(p.value);
        const current = Number((p.row as Record<string, unknown>).value);
        if (!high || !current) return "";
        return current >= high * 0.95 ? "cell-positive" : "cell-negative";
      },
      ...NUM,
    },
    {
      field: "recent_value_low_30d",
      headerName: "Val Low 30d",
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => {
        const low = Number(p.value);
        const current = Number((p.row as Record<string, unknown>).value);
        if (!low || !current) return "";
        return current > low * 1.05 ? "cell-positive" : "cell-negative";
      },
      ...NUM,
    },
    {
      field: "value_high_alltime",
      headerName: "All-Time High",
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => {
        const high = Number(p.value);
        const current = Number((p.row as Record<string, unknown>).value);
        if (!high || !current) return "";
        return current >= high * 0.95 ? "cell-positive" : "cell-negative";
      },
      ...NUM,
    },
    {
      field: "value_low_alltime",
      headerName: "All-Time Low",
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => {
        const low = Number(p.value);
        const current = Number((p.row as Record<string, unknown>).value);
        if (!low || !current) return "";
        return current > low * 1.05 ? "cell-positive" : "cell-negative";
      },
      ...NUM,
    },
    {
      field: "fx_impact",
      headerName: "FX Impact",
      width: 90,
      valueFormatter: (v) => numFmt(v),
      ...NUM,
    },
    {
      field: "tags",
      headerName: "Tags",
      width: 150,
      valueFormatter: (v) =>
        Array.isArray(v) ? (v as string[]).join(", ") : "",
    },
  ];
}

const HIDDEN_BY_DEFAULT: Record<string, boolean> = {
  data_date: false,
  volatility_50d: false,
  value_ma_50d: false,
  fx_impact: false,
  value_high_alltime: false,
  value_low_alltime: false,
};

export default function AssetTable({
  rows,
  loading = false,
  availableTags = [],
  onOpenDetails,
}: AssetTableProps) {
  const theme = useTheme();
  const { selectedTags, setSelectedTags, density } = useAppStore();

  const columns = useMemo(
    () => buildColumns(theme, onOpenDetails),
    [theme, onOpenDetails],
  );

  const positiveColor = theme.palette.success.main;
  const negativeColor = theme.palette.error.main;

  const dataDate = rows[0]?.data_date as string | undefined;

  const rowHeight = density === "comfortable" ? 44 : 34;
  const headerHeight = density === "comfortable" ? 40 : 34;

  return (
    <Box
      sx={{
        height: "100%",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        "& .cell-positive": { color: positiveColor, fontWeight: 600 },
        "& .cell-negative": { color: negativeColor, fontWeight: 600 },
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          px: 1,
          pb: 0.5,
          flexWrap: "wrap",
        }}
      >
        <Autocomplete
          multiple
          size="small"
          options={availableTags}
          value={selectedTags}
          onChange={(_, val) => setSelectedTags(val)}
          renderInput={(params) => (
            <TextField {...params} placeholder="Filter by tag..." />
          )}
          sx={{ minWidth: 220, flex: "1 1 240px" }}
          disableCloseOnSelect
        />
        {dataDate && (
          <Typography
            variant="caption"
            color="text.disabled"
            sx={{ ml: "auto", fontVariantNumeric: "tabular-nums" }}
          >
            Data as of {dataDate}
          </Typography>
        )}
      </Box>
      <Box sx={{ flex: 1, overflow: "hidden" }}>
        <DataGrid
          rows={rows}
          columns={columns}
          getRowId={(row) => row.ticker as string}
          loading={loading}
          disableRowSelectionOnClick
          getRowClassName={getRowClassName}
          density={density === "comfortable" ? "standard" : "compact"}
          rowHeight={rowHeight}
          columnHeaderHeight={headerHeight}
          columnVisibilityModel={HIDDEN_BY_DEFAULT}
          pageSizeOptions={[25, 50, 100]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } },
          }}
          sx={{
            fontSize: 12.5,
            height: "100%",
            border: "none",
            fontVariantNumeric: "tabular-nums",
            "& .MuiDataGrid-columnHeaders": {
              borderBottom: `1px solid ${theme.palette.divider}`,
            },
            "& .MuiDataGrid-columnHeader": {
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: 0.2,
              color: theme.palette.text.secondary,
              backgroundColor: theme.palette.background.paper,
            },
            "& .MuiDataGrid-columnHeader:first-of-type, & .MuiDataGrid-cell:first-of-type":
              {
                pl: 1.25,
              },
            "& .MuiDataGrid-columnHeader:last-of-type, & .MuiDataGrid-cell:last-of-type":
              {
                pr: 1.25,
              },
            "& .MuiDataGrid-columnHeaderTitle": { fontWeight: 700 },
            "& .MuiDataGrid-cell": {
              borderBottom: `1px solid ${theme.palette.divider}`,
              fontVariantNumeric: "tabular-nums",
            },
            "& .MuiDataGrid-row": {
              position: "relative",
              transition:
                "background-color 140ms ease-out, box-shadow 140ms ease-out",
            },
            "& .MuiDataGrid-row.row-odd": {
              backgroundColor: theme.custom.bgZebra,
            },
            "& .MuiDataGrid-row.row-positive": {
              backgroundColor:
                theme.palette.mode === "dark"
                  ? "rgba(34, 197, 94, 0.03)"
                  : "rgba(22, 163, 74, 0.025)",
            },
            "& .MuiDataGrid-row.row-negative": {
              backgroundColor:
                theme.palette.mode === "dark"
                  ? "rgba(239, 68, 68, 0.03)"
                  : "rgba(220, 38, 38, 0.025)",
            },
            "& .MuiDataGrid-row:hover": {
              backgroundColor: theme.custom.bgRowHover,
              boxShadow: `inset 0 0 0 1px ${theme.palette.mode === "dark" ? "rgba(107,140,255,0.12)" : "rgba(59,91,255,0.08)"}`,
            },
            "& .MuiDataGrid-row.Mui-selected": {
              backgroundColor: theme.custom.bgRowSelected,
              boxShadow: `inset 3px 0 0 0 ${theme.palette.primary.main}`,
              "&:hover": {
                backgroundColor: theme.custom.bgRowSelected,
                boxShadow: `inset 3px 0 0 0 ${theme.palette.primary.main}, inset 0 0 0 1px ${theme.palette.mode === "dark" ? "rgba(107,140,255,0.2)" : "rgba(59,91,255,0.12)"}`,
              },
            },
          }}
        />
      </Box>
    </Box>
  );
}
