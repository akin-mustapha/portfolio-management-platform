<<<<<<< HEAD
import { Box, ToggleButtonGroup, ToggleButton, Autocomplete, TextField, useTheme } from '@mui/material'
=======
import { useLayoutEffect, useRef, useState } from 'react'
import { Box, ButtonBase, useTheme } from '@mui/material'
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
import { alpha } from '@mui/material/styles'
import { useAppStore } from '../../store/useAppStore'
import { TIMEFRAME_OPTIONS } from '../../constants/timeframes'

export default function FilterBar() {
  const theme = useTheme()
  const { timeframe, setTimeframe } = useAppStore()
  const containerRef = useRef<HTMLDivElement>(null)
  const [indicator, setIndicator] = useState<{ left: number; width: number } | null>(null)

<<<<<<< HEAD
export const TIMEFRAME_OPTIONS = [
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
  { value: '1m', label: '1M' },
  { value: '3m', label: '3M' },
  { value: '6m', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: 'all', label: 'All' },
]

export default function FilterBar({ availableTags = [] }: FilterBarProps) {
  const theme = useTheme()
  const { timeframe, setTimeframe, selectedTags, setSelectedTags } = useAppStore()
=======
  useLayoutEffect(() => {
    if (!containerRef.current) return
    const active = containerRef.current.querySelector<HTMLElement>(`[data-tf="${timeframe}"]`)
    if (!active) return
    const container = containerRef.current.getBoundingClientRect()
    const rect = active.getBoundingClientRect()
    setIndicator({ left: rect.left - container.left, width: rect.width })
  }, [timeframe])
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223

  const toggleGroupSx = {
    '& .MuiToggleButton-root': {
      border: 'none',
      borderRadius: '6px',
      px: 1.5,
      py: 0.5,
      color: 'text.secondary',
      fontSize: '0.8125rem',
      fontWeight: 500,
      textTransform: 'none',
      '&.Mui-selected': {
        color: 'primary.main',
        bgcolor: alpha(theme.palette.primary.main, 0.12),
        '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.18) },
      },
      '&:hover': { bgcolor: 'action.hover' },
    },
  }

  return (
    <Box sx={{
      display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap',
      border: '1px solid', borderColor: 'divider',
<<<<<<< HEAD
      borderRadius: 1, px: 1.5, py: 0.75, mb: 1,
    }}>
      <ToggleButtonGroup
        value={timeframe}
        exclusive
        onChange={(_, val) => { if (val) setTimeframe(val) }}
        size="small"
        sx={toggleGroupSx}
      >
        {TIMEFRAME_OPTIONS.map((o) => (
          <ToggleButton key={o.value} value={o.value}>
            {o.label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>

      <Autocomplete
        multiple
        size="small"
        options={availableTags}
        value={selectedTags}
        onChange={(_, val) => setSelectedTags(val)}
        renderInput={(params) => <TextField {...params} placeholder="Filter by tag..." />}
        sx={{ minWidth: 220 }}
        disableCloseOnSelect
      />
=======
      borderRadius: 3, px: 0.75, py: 0.5, mb: 1,
      bgcolor: 'background.paper',
    }}>
      <Box
        ref={containerRef}
        sx={{ position: 'relative', display: 'flex', gap: 0.25, p: 0.25 }}
      >
        {indicator && (
          <Box
            sx={{
              position: 'absolute',
              top: 4,
              bottom: 4,
              left: indicator.left,
              width: indicator.width,
              borderRadius: 1.25,
              bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.18 : 0.12),
              border: `1px solid ${alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.32 : 0.22)}`,
              transition: 'left 220ms cubic-bezier(0.4, 0, 0.2, 1), width 220ms cubic-bezier(0.4, 0, 0.2, 1)',
              pointerEvents: 'none',
              zIndex: 0,
            }}
          />
        )}
        {TIMEFRAME_OPTIONS.map((o) => {
          const active = timeframe === o.value
          return (
            <ButtonBase
              key={o.value}
              data-tf={o.value}
              onClick={() => setTimeframe(o.value)}
              sx={{
                position: 'relative',
                zIndex: 1,
                px: 1.5,
                py: 0.5,
                borderRadius: 1.25,
                fontSize: '0.8125rem',
                fontWeight: active ? 600 : 500,
                color: active ? 'primary.main' : 'text.secondary',
                transition: 'color 180ms ease',
                '&:hover': { color: active ? 'primary.main' : 'text.primary' },
              }}
            >
              {o.label}
            </ButtonBase>
          )
        })}
      </Box>
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
    </Box>
  )
}
