import { useState } from 'react'
import { Box, Divider, IconButton, Popover, Typography } from '@mui/material'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import { metricDefinitions, type MetricKey } from '../../constants/metricDefinitions'

interface MetricInfoProps {
  metricKey: MetricKey
  size?: 'small' | 'inherit'
}

export default function MetricInfo({ metricKey, size = 'small' }: MetricInfoProps) {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null)

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation()
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => setAnchorEl(null)

  const open = Boolean(anchorEl)
  const { title, definition, interpret } = metricDefinitions[metricKey]

  return (
    <>
      <IconButton
        size="small"
        onClick={handleClick}
        sx={{
          p: 0,
          color: 'text.disabled',
          '&:hover': { color: 'text.secondary', backgroundColor: 'transparent' },
        }}
      >
        <InfoOutlinedIcon fontSize={size} sx={{ fontSize: size === 'inherit' ? '0.85em' : 14 }} />
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        disableRestoreFocus
      >
        <Box sx={{ p: 1.5, maxWidth: 280 }}>
          <Typography variant="subtitle2" fontWeight={700} gutterBottom>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {definition}
          </Typography>
          <Divider sx={{ my: 1 }} />
          <Typography variant="caption" color="text.secondary" display="block">
            {interpret}
          </Typography>
        </Box>
      </Popover>
    </>
  )
}
