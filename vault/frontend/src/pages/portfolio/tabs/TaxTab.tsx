import { useTheme, Box, Typography } from "@mui/material";

export default function TaxTab() {
  const theme = useTheme();
  return (
    <Box sx={{ padding: "32px 32px 40px" }}>
      <div
        style={{
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: ".1em",
          textTransform: "uppercase",
          color: theme.palette.text.secondary,
        }}
      >
        Tax
      </div>
      <Typography
        variant="h4"
        fontWeight={700}
        letterSpacing="-0.025em"
        sx={{ mt: "4px", mb: 2 }}
      >
        Tax overview
      </Typography>
      <Box
        sx={{
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 3,
          bgcolor: "background.paper",
          p: 4,
          textAlign: "center",
          color: "text.secondary",
        }}
      >
        <Typography variant="body2">Tax reporting coming soon.</Typography>
      </Box>
    </Box>
  );
}
