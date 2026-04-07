import { Box, FormControl, InputLabel, MenuItem, Select, Autocomplete, TextField } from '@mui/material'
import { useAppStore } from '../../store/useAppStore'

interface FilterBarProps {
  availableTags?: string[]
}

const TIMEFRAME_OPTIONS = [
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
  { value: '180d', label: '6 Months' },
  { value: '365d', label: '1 Year' },
  { value: 'all', label: 'All Time' },
]

export default function FilterBar({ availableTags = [] }: FilterBarProps) {
  const { timeframe, setTimeframe, selectedTags, setSelectedTags } = useAppStore()

  return (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
      <FormControl size="small" sx={{ minWidth: 120 }}>
        <InputLabel>Timeframe</InputLabel>
        <Select
          value={timeframe}
          label="Timeframe"
          onChange={(e) => setTimeframe(e.target.value as Parameters<typeof setTimeframe>[0])}
        >
          {TIMEFRAME_OPTIONS.map((o) => (
            <MenuItem key={o.value} value={o.value}>
              {o.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Autocomplete
        multiple
        size="small"
        options={availableTags}
        value={selectedTags}
        onChange={(_, val) => setSelectedTags(val)}
        renderInput={(params) => <TextField {...params} label="Tags" placeholder="Filter by tag…" />}
        sx={{ minWidth: 220 }}
        disableCloseOnSelect
      />
    </Box>
  )
}
