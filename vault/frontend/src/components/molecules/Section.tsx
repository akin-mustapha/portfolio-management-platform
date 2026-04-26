import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Typography,
} from "@mui/material";
import type { SxProps, Theme } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import type { ReactNode } from "react";
import MetricInfo from "../atoms/MetricInfo";
import type { MetricKey } from "../../constants/metricDefinitions";

interface SectionProps {
  title: string;
  children: ReactNode;
  metricKey?: MetricKey;
  sx?: SxProps<Theme>;
}

export default function Section({
  title,
  children,
  metricKey,
  sx,
}: SectionProps) {
  return (
    <Accordion
      defaultExpanded
      disableGutters
      elevation={0}
      sx={[
        (theme) => ({
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 3,
          mb: 1,
          overflow: "hidden",
          bgcolor: "background.paper",
          boxShadow: theme.custom.shadowCard,
          transition: "box-shadow 180ms ease, border-color 180ms ease",
          "&:hover": { boxShadow: theme.custom.shadowCardHover },
          "&:before": { display: "none" },
        }),
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        sx={{ minHeight: 36, "& .MuiAccordionSummary-content": { my: 0.5 } }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, flex: 1 }}>
          <Typography variant="subtitle2" fontWeight={600}>
            {title}
          </Typography>
          {metricKey && <MetricInfo metricKey={metricKey} />}
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 1, minWidth: 0, overflow: "hidden" }}>
        {children}
      </AccordionDetails>
    </Accordion>
  );
}
