import { Box, Card, CardContent, Skeleton, Typography, useTheme } from '@mui/material'
import PrivacyValue from './PrivacyValue'

interface KpiCardProps {
  label: string
  value?: number | string | null
  subValue?: string | null
  prefix?: string
  suffix?: string
  colorCode?: 'positive' | 'negative' | 'neutral'
  loading?: boolean
  compact?: boolean
}

export default function KpiCard({
  label,
  value,
  subValue,
  prefix = '',
  suffix = '',
  colorCode = 'neutral',
  loading = false,
  compact = false,
}: KpiCardProps) {
  const theme = useTheme()
  const colorMap = {
    positive: theme.palette.success.main,
    negative: theme.palette.error.main,
    neutral: theme.palette.text.primary,
  }
  const valueColor = colorMap[colorCode]

  return (
    <Card
      variant="outlined"
      sx={{
        height: '100%',
        minWidth: compact ? 120 : 140,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}
    >
      <CardContent sx={{ p: compact ? 1 : 1.5, '&:last-child': { pb: compact ? 1 : 1.5 } }}>
        <Typography variant="caption" color="text.secondary" noWrap display="block" gutterBottom>
          {label}
        </Typography>
        {loading ? (
          <Skeleton width="80%" height={28} />
        ) : (
          <Box>
            <Typography
              variant={compact ? 'body2' : 'h6'}
              fontWeight={700}
              sx={{ color: valueColor, lineHeight: 1.2 }}
            >
              {value != null ? (
                <PrivacyValue
                  value={`${prefix}${
                    typeof value === 'number'
                      ? value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                      : value
                  }${suffix}`}
                />
              ) : (
                '—'
              )}
            </Typography>
            {subValue && (
              <Typography variant="caption" color="text.secondary">
                {subValue}
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
