import {
  DataGrid,
  type GridColDef,
  type GridRenderCellParams,
  type GridRowSelectionModel,
} from '@mui/x-data-grid'
import { Box, useTheme } from '@mui/material'
import { useAppStore } from '../../store/useAppStore'
import SparklineChart from '../charts/SparklineChart'

interface AssetTableProps {
  rows: Record<string, unknown>[]
  loading?: boolean
}

function numFmt(v: unknown, decimals = 2) {
  if (v == null) return '—'
  return Number(v).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

function pctFmt(v: unknown) {
  if (v == null) return '—'
  return `${Number(v).toFixed(2)}%`
}

const COLUMNS: GridColDef[] = [
  { field: 'ticker', headerName: 'Ticker', width: 90, pinnable: true },
  { field: 'name', headerName: 'Name', width: 160, flex: 1 },
  { field: 'price', headerName: 'Price', width: 90, valueFormatter: (v) => numFmt(v) },
  { field: 'avg_price', headerName: 'Avg Price', width: 90, valueFormatter: (v) => numFmt(v) },
  { field: 'value', headerName: 'Value', width: 110, valueFormatter: (v) => numFmt(v) },
  { field: 'cost', headerName: 'Cost', width: 110, valueFormatter: (v) => numFmt(v) },
  {
    field: 'profit',
    headerName: 'P&L',
    width: 110,
    valueFormatter: (v) => numFmt(v),
    cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
  },
  {
    field: 'pnl_pct',
    headerName: 'P&L %',
    width: 90,
    valueFormatter: pctFmt,
    cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
  },
  { field: 'weight_pct', headerName: 'Weight %', width: 90, valueFormatter: pctFmt },
  {
    field: 'daily_value_return',
    headerName: 'Daily Return',
    width: 100,
    valueFormatter: (v) => (v != null ? `${(Number(v) * 100).toFixed(2)}%` : '—'),
    cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
  },
  { field: 'cumulative_value_return', headerName: 'Cum. Return', width: 110, valueFormatter: pctFmt },
  { field: 'volatility_30d', headerName: 'Vol 30d', width: 90, valueFormatter: (v) => numFmt(v, 4) },
  { field: 'volatility_50d', headerName: 'Vol 50d', width: 90, valueFormatter: (v) => numFmt(v, 4) },
  { field: 'var_95_1d', headerName: 'VaR 95%', width: 90, valueFormatter: (v) => numFmt(v, 4) },
  { field: 'beta_60d', headerName: 'Beta 60d', width: 90, valueFormatter: (v) => numFmt(v, 3) },
  { field: 'asset_sharpe_ratio_30d', headerName: 'Sharpe', width: 80, valueFormatter: (v) => numFmt(v, 2) },
  { field: 'value_ma_30d', headerName: 'MA 30d', width: 90, valueFormatter: (v) => numFmt(v) },
  { field: 'value_ma_50d', headerName: 'MA 50d', width: 90, valueFormatter: (v) => numFmt(v) },
  { field: 'value_drawdown_pct_30d', headerName: 'Drawdown 30d', width: 120, valueFormatter: pctFmt },
  { field: 'recent_profit_high_30d', headerName: 'P&L High 30d', width: 120, valueFormatter: (v) => numFmt(v) },
  { field: 'recent_profit_low_30d', headerName: 'P&L Low 30d', width: 120, valueFormatter: (v) => numFmt(v) },
  { field: 'dca_bias', headerName: 'DCA Bias', width: 90, valueFormatter: (v) => numFmt(v, 4) },
  { field: 'fx_impact', headerName: 'FX Impact', width: 90, valueFormatter: (v) => numFmt(v) },
  { field: 'trend', headerName: 'Trend', width: 90 },
  {
    field: 'tags',
    headerName: 'Tags',
    width: 150,
    valueFormatter: (v) => (Array.isArray(v) ? (v as string[]).join(', ') : ''),
  },
  {
    field: 'price_series',
    headerName: 'Price Sparkline',
    width: 100,
    sortable: false,
    filterable: false,
    renderCell: (params: GridRenderCellParams) => {
      const values = params.value as (number | null)[] | undefined
      if (!values?.length) return null
      const last = values.filter((v) => v != null)
      const sentiment = last.length >= 2
        ? last[last.length - 1]! >= last[0]! ? 'positive' : 'negative'
        : 'neutral'
      return <SparklineChart values={values} sentiment={sentiment} height={32} />
    },
  },
]

function selectionToTickers(model: GridRowSelectionModel): string[] {
  if (model.type === 'exclude') return []
  return Array.from(model.ids) as string[]
}

function tickersToSelection(tickers: string[]): GridRowSelectionModel {
  return { type: 'include', ids: new Set(tickers) }
}

export default function AssetTable({ rows, loading = false }: AssetTableProps) {
  const theme = useTheme()
  const { selectedTickers, setSelectedTickers } = useAppStore()

  const positiveColor = theme.palette.success.main
  const negativeColor = theme.palette.error.main

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        '& .cell-positive': { color: positiveColor, fontWeight: 600 },
        '& .cell-negative': { color: negativeColor, fontWeight: 600 },
      }}
    >
      <DataGrid
        rows={rows}
        columns={COLUMNS}
        getRowId={(row) => row.ticker as string}
        loading={loading}
        checkboxSelection
        disableRowSelectionOnClick
        rowSelectionModel={tickersToSelection(selectedTickers)}
        onRowSelectionModelChange={(model) => setSelectedTickers(selectionToTickers(model))}
        density="compact"
        columnVisibilityModel={{ data_date: false }}
        pageSizeOptions={[25, 50, 100]}
        initialState={{
          pagination: { paginationModel: { pageSize: 25 } },
        }}
        sx={{
          fontSize: 12,
          '& .MuiDataGrid-columnHeader': {
            fontSize: 11,
            fontWeight: 700,
            backgroundColor: theme.palette.background.default,
          },
        }}
      />
    </Box>
  )
}
