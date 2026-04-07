import { Box, Typography } from '@mui/material'
import { useAppStore } from '../../store/useAppStore'

export default function StatusBar() {
  const selectedTickers = useAppStore((s) => s.selectedTickers)

  if (selectedTickers.length === 0) return null

  return (
    <Box sx={{ px: 1, py: 0.5 }}>
      <Typography variant="caption" color="text.secondary">
        {selectedTickers.length} asset{selectedTickers.length !== 1 ? 's' : ''} selected:{' '}
        {selectedTickers.join(', ')}
      </Typography>
    </Box>
  )
}
