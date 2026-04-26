import { useState } from "react";
import {
  Box,
  Button,
  Chip,
  Divider,
  IconButton,
  Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import AssetProfileTab from "../../pages/portfolio/tabs/AssetProfileTab";
import TickerLogo from "../atoms/TickerLogo";
import EditTagsModal from "./EditTagsModal";
import { usePortfolioContext } from "../../pages/portfolio/PortfolioContext";

interface AssetProfileDrawerProps {
  open: boolean;
  onClose: () => void;
}

const PANEL_WIDTH = 480;

export default function AssetProfileDrawer({
  open,
  onClose,
}: AssetProfileDrawerProps) {
  const { selectedAssetRow: assetRow } = usePortfolioContext();
  const [tagsOpen, setTagsOpen] = useState(false);
  if (!open) return null;

  const ticker = assetRow?.ticker as string | undefined;
  const name = assetRow?.name as string | undefined;
  const tags = (assetRow?.tags as string[]) ?? [];

  return (
    <Box
      sx={{
        width: PANEL_WIDTH,
        flexShrink: 0,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        borderLeft: "1px solid",
        borderColor: "divider",
        bgcolor: "background.default",
        animation: "panelSlideIn 220ms cubic-bezier(0.4, 0, 0.2, 1)",
        "@keyframes panelSlideIn": {
          from: { transform: "translateX(16px)", opacity: 0 },
          to: { transform: "translateX(0)", opacity: 1 },
        },
      }}
    >
      <Box
        sx={(theme) => ({
          mx: 2,
          mt: 2,
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 3,
          bgcolor: "background.paper",
          boxShadow: theme.custom.shadowCard,
          overflow: "hidden",
          transition: "box-shadow 180ms ease",
          "&:hover": { boxShadow: theme.custom.shadowCardHover },
        })}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            px: 2,
            py: 1.25,
          }}
        >
          <Typography
            variant="caption"
            sx={{
              textTransform: "uppercase",
              letterSpacing: 1,
              fontWeight: 700,
              color: "text.secondary",
              fontSize: 10.5,
            }}
          >
            Asset Profile
          </Typography>
          <IconButton
            size="small"
            onClick={onClose}
            sx={{
              transition: "transform 160ms ease, color 160ms ease",
              "&:hover": { color: "text.primary" },
            }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
        {ticker && (
          <>
            <Divider />
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                flexWrap: "wrap",
                px: 2,
                py: 1.25,
              }}
            >
              <TickerLogo ticker={ticker} size={28} />
              <Typography
                variant="subtitle1"
                sx={{ fontWeight: 700, letterSpacing: "-0.01em" }}
                component="div"
              >
                {ticker}
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ flex: 1, minWidth: 0 }}
                noWrap
              >
                {name}
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  gap: 0.5,
                  flexWrap: "wrap",
                  alignItems: "center",
                }}
              >
                {tags.map((t) => (
                  <Chip
                    key={t}
                    label={t}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: 10 }}
                  />
                ))}
                <Button
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: 10, height: 24 }}
                  onClick={() => setTagsOpen(true)}
                >
                  Edit Tags
                </Button>
              </Box>
            </Box>
          </>
        )}
      </Box>
      <Box sx={{ flex: 1, overflow: "auto", px: 2, pt: 1.5, pb: 2 }}>
        <AssetProfileTab />
      </Box>
      {ticker && (
        <EditTagsModal
          open={tagsOpen}
          onClose={() => setTagsOpen(false)}
          ticker={ticker}
          currentTags={tags}
        />
      )}
    </Box>
  );
}
