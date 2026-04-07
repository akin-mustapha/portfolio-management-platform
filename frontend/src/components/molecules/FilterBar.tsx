import { Box, ToggleButtonGroup, ToggleButton, Autocomplete, TextField, useTheme } from '@mui/material'
import { alpha } from '@mui/material/styles'
import { useAppStore } from '../../store/useAppStore'

interface FilterBarProps {
  availableTags?: string[]
}

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
    </Box>
  )
}
