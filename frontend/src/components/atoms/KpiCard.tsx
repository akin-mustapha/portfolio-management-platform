import { Box, Skeleton, Typography, useTheme } from '@mui/material'
import PrivacyValue from './PrivacyValue'
import MetricInfo from './MetricInfo'
import SparklineChart from '../charts/SparklineChart'
import type { MetricKey } from '../../constants/metricDefinitions'

type Variant = 'default' | 'compact' | 'hero'

interface KpiCardProps {
  label: string
  value?: number | string | null
  subValue?: string | null
  prefix?: string
  suffix?: string
  colorCode?: 'positive' | 'negative' | 'neutral'
  loading?: boolean
  compact?: boolean
  variant?: Variant
  metricKey?: MetricKey
  sparkline?: (number | null)[]
  /** Render a bordered card frame (useful for standalone metric tiles) */
  bordered?: boolean
  /** Reserve bottom space for a sparkline even when none is provided (baseline alignment) */
  reserveSparklineSlot?: boolean
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
  variant,
  metricKey,
  sparkline,
  bordered = false,
  reserveSparklineSlot = true,
}: KpiCardProps) {
  const theme = useTheme()
  const resolvedVariant: Variant = variant ?? (compact ? 'compact' : 'default')
  const isHero = resolvedVariant === 'hero'
  const isCompact = resolvedVariant === 'compact'

  const heroNeutral = theme.palette.mode === 'dark' ? '#ffffff' : '#000000'
  const colorMap = {
    positive: theme.palette.success.main,
    negative: theme.palette.error.main,
    neutral: isHero ? heroNeutral : theme.palette.text.primary,
  }
  const valueColor = colorMap[colorCode]

  const labelSize = isHero ? 11.5 : 10.5
  const valueStyles = isHero
    ? { fontSize: 40, fontWeight: 700, letterSpacing: '-0.025em', lineHeight: 1.02 }
    : isCompact
      ? { fontSize: 14, fontWeight: 600, letterSpacing: '-0.005em', lineHeight: 1.25 }
      : { fontSize: 18, fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.2 }
  const pad = isHero ? 2.25 : isCompact ? 0.75 : 1.5

  const hasSparkline = !!(sparkline && sparkline.length > 0)
  const sparklineSlotHeight = isHero ? 64 : isCompact ? 22 : 32

  return (
    <Box
      sx={{
        height: '100%',
<<<<<<< HEAD
        minWidth: compact ? 115 : 140,
=======
        minWidth: isCompact ? 110 : isHero ? 220 : 140,
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
        display: 'flex',
        flexDirection: 'column',
        justifyContent: isHero ? 'flex-start' : 'center',
        p: pad,
        pb: isHero ? 0 : pad,
        bgcolor: isHero || bordered ? 'background.paper' : 'transparent',
        border: isHero || bordered ? '1px solid' : 'none',
        borderColor: 'divider',
        borderRadius: isHero || bordered ? 2 : 0,
        transition: 'background-color 160ms ease, border-color 160ms ease, box-shadow 160ms ease',
        '&:hover': bordered
          ? (theme) => ({ borderColor: 'divider', boxShadow: theme.custom.shadowCardHover })
          : isCompact
            ? { bgcolor: 'action.hover' }
            : undefined,
      }}
    >
<<<<<<< HEAD
      <CardContent sx={{ p: compact ? 1.25 : 1.5, '&:last-child': { pb: compact ? 1.25 : 1.5 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25 }} mb={0.5}>
          <Typography variant="caption" color="text.secondary" noWrap>
            {label}
          </Typography>
          {metricKey && <MetricInfo metricKey={metricKey} size="inherit" />}
        </Box>
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
=======
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25, mb: isHero ? 1 : 0.5 }}>
        <Typography
          variant="caption"
          color="text.secondary"
          noWrap
          sx={{
            fontSize: labelSize,
            letterSpacing: isHero ? 0.4 : 0.2,
            textTransform: isHero ? 'uppercase' : 'none',
            fontWeight: isHero ? 600 : 500,
          }}
        >
          {label}
        </Typography>
        {metricKey && <MetricInfo metricKey={metricKey} size="inherit" />}
      </Box>
      {loading ? (
        <Skeleton width="80%" height={isHero ? 40 : 24} />
      ) : (
        <>
          <Typography sx={{ color: valueColor, ...valueStyles, fontVariantNumeric: 'tabular-nums' }}>
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
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
            )}
          </Typography>
          {subValue && (
            <Typography variant="caption" color="text.secondary" sx={{ fontVariantNumeric: 'tabular-nums' }}>
              {subValue}
            </Typography>
          )}
          {(hasSparkline || (isCompact && reserveSparklineSlot)) && (
            <Box
              sx={{
                mt: isHero ? 'auto' : 0,
                pt: isHero ? 1.25 : 0.5,
                mx: isHero ? -1 : -0.5,
                minHeight: sparklineSlotHeight,
                display: 'flex',
                alignItems: 'flex-end',
              }}
            >
              {hasSparkline && (
                <Box sx={{ width: '100%' }}>
                  <SparklineChart
                    values={sparkline}
                    sentiment={colorCode}
                    height={sparklineSlotHeight}
                    fill
                  />
                </Box>
              )}
            </Box>
          )}
        </>
      )}
    </Box>
  )
}
