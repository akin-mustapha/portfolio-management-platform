import { useMemo } from 'react'
import {
  DataGrid,
  type GridColDef,
  type GridRenderCellParams,
  type GridRowSelectionModel,
} from '@mui/x-data-grid'
import { Box, Chip, Typography, useTheme, type Theme } from '@mui/material'
import { useAppStore } from '../../store/useAppStore'
import SparklineChart from '../charts/SparklineChart'
import MetricInfo from '../atoms/MetricInfo'

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

function headerWithInfo(label: string, metricKey: Parameters<typeof MetricInfo>[0]['metricKey']) {
  return () => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <span style={{ fontSize: 11, fontWeight: 700 }}>{label}</span>
      <MetricInfo metricKey={metricKey} />
    </Box>
  )
}

function buildColumns(theme: Theme): GridColDef[] {
  return [
    {
      field: 'price_series',
      headerName: '',
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
    { field: 'ticker', headerName: 'Ticker', width: 90, pinnable: true },
    { field: 'name', headerName: 'Name', width: 220 },
    { field: 'price', headerName: 'Price', width: 90, valueFormatter: (v) => numFmt(v) },
    { field: 'avg_price', headerName: 'Avg Price', width: 90, valueFormatter: (v) => numFmt(v), renderHeader: headerWithInfo('Avg Price', 'avg_price') },
    {
      field: 'price_vs_avg_pct',
      headerName: 'vs Avg %',
      width: 90,
      valueGetter: (_value: unknown, row: Record<string, unknown>) => {
        const price = Number(row.price)
        const avg = Number(row.avg_price)
        if (!avg) return null
        return ((price - avg) / avg) * 100
      },
      valueFormatter: pctFmt,
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
    },
    { field: 'value', headerName: 'Value', width: 110, valueFormatter: (v) => numFmt(v) },
    { field: 'cost', headerName: 'Cost', width: 110, valueFormatter: (v) => numFmt(v) },
    {
      field: 'profit',
      headerName: 'P&L',
      width: 110,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('P&L', 'profit'),
    },
    {
      field: 'pnl_pct',
      headerName: 'P&L %',
      width: 90,
      valueFormatter: pctFmt,
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('P&L %', 'pnl_pct'),
    },
    { field: 'weight_pct', headerName: 'Weight %', width: 90, valueFormatter: pctFmt, renderHeader: headerWithInfo('Weight %', 'weight_pct') },
    {
      field: 'daily_value_return',
      headerName: 'Daily Return',
      width: 100,
      valueFormatter: (v) => (v != null ? `${(Number(v) * 100).toFixed(2)}%` : '—'),
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('Daily Return', 'daily_value_return'),
    },
    {
      field: 'cumulative_value_return',
      headerName: 'Cum. Return',
      width: 110,
      valueFormatter: pctFmt,
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('Cum. Return', 'cumulative_value_return'),
    },
    {
      field: 'trend',
      headerName: 'Trend',
      width: 100,
      renderHeader: headerWithInfo('Trend', 'trend'),
      renderCell: (params: GridRenderCellParams) => {
        const val = params.value as string
        const isBullish = val === 'Bullish'
        return (
          <Chip
            label={val}
            size="small"
            sx={{
              height: 20,
              fontSize: 10,
              fontWeight: 700,
              bgcolor: isBullish ? theme.palette.success.main : theme.palette.error.main,
              color: '#fff',
            }}
          />
        )
      },
    },
    {
      field: 'dca_bias',
      headerName: 'DCA Bias',
      width: 90,
      valueFormatter: (v) => numFmt(v, 4),
      cellClassName: (p) => (Number(p.value) < 1 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('DCA Bias', 'dca_bias'),
    },
    { field: 'volatility_30d', headerName: 'Vol 30d', width: 90, valueFormatter: (v) => numFmt(v, 4), renderHeader: headerWithInfo('Vol 30d', 'volatility_30d') },
    { field: 'volatility_50d', headerName: 'Vol 50d', width: 90, valueFormatter: (v) => numFmt(v, 4) },
    { field: 'var_95_1d', headerName: 'VaR 95%', width: 90, valueFormatter: (v) => numFmt(v, 4), renderHeader: headerWithInfo('VaR 95%', 'var_95_1d') },
    {
      field: 'beta_60d',
      headerName: 'Beta 60d',
      width: 90,
      valueFormatter: (v) => numFmt(v, 3),
      // > 1 = amplifies market moves (more risk), ≤ 1 = less market sensitivity
      cellClassName: (p) => (p.value != null ? (Number(p.value) > 1 ? 'cell-negative' : 'cell-positive') : ''),
    },
    {
      field: 'asset_sharpe_ratio_30d',
      headerName: 'Sharpe',
      width: 80,
      valueFormatter: (v) => numFmt(v, 2),
      // > 1 = good risk-adjusted return, 0–1 = acceptable, < 0 = losing vs risk-free
      cellClassName: (p) => (p.value != null ? (Number(p.value) >= 1 ? 'cell-positive' : 'cell-negative') : ''),
    },
    { field: 'value_ma_30d', headerName: 'MA 30d', width: 90, valueFormatter: (v) => numFmt(v) },
    { field: 'value_ma_50d', headerName: 'MA 50d', width: 90, valueFormatter: (v) => numFmt(v) },
    {
      field: 'value_drawdown_pct_30d',
      headerName: 'Drawdown 30d',
      width: 120,
      valueFormatter: pctFmt,
      // drawdown is 0 or negative — 0 means at peak (good), negative means below peak
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('Drawdown 30d', 'value_drawdown_pct_30d'),
    },
    {
      field: 'recent_profit_high_30d',
      headerName: 'P&L High 30d',
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
      renderHeader: headerWithInfo('P&L High 30d', 'recent_profit_high_30d'),
    },
    {
      field: 'recent_profit_low_30d',
      headerName: 'P&L Low 30d',
      width: 120,
      valueFormatter: (v) => numFmt(v),
      cellClassName: (p) => (Number(p.value) >= 0 ? 'cell-positive' : 'cell-negative'),
    },
    {
      field: 'recent_value_high_30d',
      headerName: 'Val High 30d',
      width: 120,
      valueFormatter: (v) => numFmt(v),
      // green when current value is at or near the 30d high (within 5%), red when meaningfully below
      cellClassName: (p) => {
        const high = Number(p.value)
        const current = Number((p.row as Record<string, unknown>).value)
        if (!high || !current) return ''
        return current >= high * 0.95 ? 'cell-positive' : 'cell-negative'
      },
    },
    {
      field: 'recent_value_low_30d',
      headerName: 'Val Low 30d',
      width: 120,
      valueFormatter: (v) => numFmt(v),
      // green when current value is well above the 30d low (more than 5% above), red when near the low
      cellClassName: (p) => {
        const low = Number(p.value)
        const current = Number((p.row as Record<string, unknown>).value)
        if (!low || !current) return ''
        return current > low * 1.05 ? 'cell-positive' : 'cell-negative'
      },
    },
    {
      field: 'value_high_alltime',
      headerName: 'All-Time High',
      width: 120,
      valueFormatter: (v) => numFmt(v),
      // green when current value is at or near all-time high (within 5%)
      cellClassName: (p) => {
        const high = Number(p.value)
        const current = Number((p.row as Record<string, unknown>).value)
        if (!high || !current) return ''
        return current >= high * 0.95 ? 'cell-positive' : 'cell-negative'
      },
    },
    {
      field: 'value_low_alltime',
      headerName: 'All-Time Low',
      width: 120,
      valueFormatter: (v) => numFmt(v),
      // green when current value is well above all-time low (more than 5% above)
      cellClassName: (p) => {
        const low = Number(p.value)
        const current = Number((p.row as Record<string, unknown>).value)
        if (!low || !current) return ''
        return current > low * 1.05 ? 'cell-positive' : 'cell-negative'
      },
    },
    { field: 'fx_impact', headerName: 'FX Impact', width: 90, valueFormatter: (v) => numFmt(v) },
    {
      field: 'tags',
      headerName: 'Tags',
      width: 150,
      valueFormatter: (v) => (Array.isArray(v) ? (v as string[]).join(', ') : ''),
    },
  ]
}

const HIDDEN_BY_DEFAULT: Record<string, boolean> = {
  data_date: false,
  volatility_50d: false,
  value_ma_50d: false,
  fx_impact: false,
  value_high_alltime: false,
  value_low_alltime: false,
}

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

  const columns = useMemo(() => buildColumns(theme), [theme])

  const positiveColor = theme.palette.success.main
  const negativeColor = theme.palette.error.main

  const dataDate = rows[0]?.data_date as string | undefined

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        '& .cell-positive': { color: positiveColor, fontWeight: 600 },
        '& .cell-negative': { color: negativeColor, fontWeight: 600 },
      }}
    >
      {dataDate && (
        <Typography variant="caption" color="text.disabled" sx={{ px: 1, pb: 0.5 }}>
          Data as of {dataDate}
        </Typography>
      )}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          getRowId={(row) => row.ticker as string}
          loading={loading}
          checkboxSelection
          disableRowSelectionOnClick
          rowSelectionModel={tickersToSelection(selectedTickers)}
          onRowSelectionModelChange={(model) => setSelectedTickers(selectionToTickers(model))}
          density="compact"
          columnVisibilityModel={HIDDEN_BY_DEFAULT}
          pageSizeOptions={[25, 50, 100]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } },
          }}
          sx={{
            fontSize: 12,
            height: '100%',
            '& .MuiDataGrid-columnHeader': {
              fontSize: 11,
              fontWeight: 700,
              backgroundColor: theme.palette.background.default,
            },
          }}
        />
      </Box>
    </Box>
  )
}
