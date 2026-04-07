import { Accordion, AccordionDetails, AccordionSummary, Typography } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import type { ReactNode } from 'react'

interface SectionProps {
  title: string
  children: ReactNode
}

export default function Section({ title, children }: SectionProps) {
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
        <Typography variant="subtitle2" fontWeight={600}>{title}</Typography>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 1 }}>{children}</AccordionDetails>
    </Accordion>
  )
}
