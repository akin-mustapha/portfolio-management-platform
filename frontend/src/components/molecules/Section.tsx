import { Accordion, AccordionDetails, AccordionSummary, Box, Typography } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import type { ReactNode } from 'react'
import MetricInfo from '../atoms/MetricInfo'
import type { MetricKey } from '../../constants/metricDefinitions'

interface SectionProps {
  title: string
  children: ReactNode
  metricKey?: MetricKey
}

export default function Section({ title, children, metricKey }: SectionProps) {
  return (
    <Accordion
      defaultExpanded
      disableGutters
      elevation={0}
      sx={{ border: '1px solid', borderColor: 'divider', mb: 1, '&:before': { display: 'none' } }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        sx={{ minHeight: 36, '& .MuiAccordionSummary-content': { my: 0.5 } }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flex: 1 }}>
          <Typography variant="subtitle2" fontWeight={600}>{title}</Typography>
          {metricKey && <MetricInfo metricKey={metricKey} />}
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 1 }}>{children}</AccordionDetails>
    </Accordion>
  )
}
