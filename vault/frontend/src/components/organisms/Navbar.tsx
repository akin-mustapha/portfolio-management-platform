import { useState } from "react";
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import { NavLink } from "react-router-dom";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import SettingsIcon from "@mui/icons-material/Settings";
import BalanceIcon from "@mui/icons-material/Balance";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import DensitySmallIcon from "@mui/icons-material/DensitySmall";
import DensityMediumIcon from "@mui/icons-material/DensityMedium";
import { useAppStore } from "../../store/useAppStore";

interface NavbarProps {
  onSettingsOpen: () => void;
  onRebalanceOpen: () => void;
  onProfileToggle: () => void;
  profileOpen: boolean;
}

const NAV_LINKS = [
  { to: "/portfolio", label: "Portfolio" },
  { to: "/performance", label: "Performance" },
  { to: "/risk", label: "Risk" },
  { to: "/opportunities", label: "Opportunities" },
  { to: "/tax", label: "Tax" },
];

export default function Navbar({
  onSettingsOpen,
  onRebalanceOpen,
  onProfileToggle,
  profileOpen,
}: NavbarProps) {
  const {
    themeMode,
    toggleTheme,
    privacyMode,
    togglePrivacy,
    density,
    toggleDensity,
  } = useAppStore();
  const [menuEl, setMenuEl] = useState<HTMLElement | null>(null);
  const menuOpen = Boolean(menuEl);

  const closeMenu = () => setMenuEl(null);

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: "background.paper",
        borderBottom: "1px solid",
        borderColor: "divider",
        color: "text.primary",
      }}
    >
      <Toolbar variant="dense" sx={{ gap: 2, minHeight: "56px !important" }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1.25,
            flexShrink: 0,
          }}
        >
          <Box
            sx={{
              width: 22,
              height: 22,
              borderRadius: 1.5,
              bgcolor: "primary.main",
              display: "grid",
              placeItems: "center",
              color: "#fff",
              fontSize: 13,
              fontWeight: 700,
            }}
          >
            L
          </Box>
          <Typography
            variant="subtitle1"
            fontWeight={700}
            letterSpacing="-0.02em"
          >
            Ledger
          </Typography>
        </Box>

        <Box sx={{ display: "flex", gap: 0.5, flexGrow: 1, ml: 2 }}>
          {NAV_LINKS.map((link) => (
            <Box
              key={link.to}
              component={NavLink}
              to={link.to}
              sx={{
                position: "relative",
                px: 1.25,
                py: 0.75,
                fontSize: 13,
                fontWeight: 500,
                color: "text.secondary",
                textDecoration: "none",
                transition: "color 160ms ease",
                "&:hover": { color: "text.primary" },
                "&::after": {
                  content: '""',
                  position: "absolute",
                  left: 10,
                  right: 10,
                  bottom: 2,
                  height: 2,
                  borderRadius: 2,
                  bgcolor: "primary.main",
                  transform: "scaleX(0)",
                  transformOrigin: "center",
                  transition: "transform 180ms ease",
                },
                "&.active": {
                  color: "primary.main",
                },
                "&.active::after": {
                  transform: "scaleX(1)",
                },
              }}
            >
              {link.label}
            </Box>
          ))}
        </Box>

        <Box sx={{ display: "flex", gap: 0.5, alignItems: "center" }}>
          <Tooltip
            title={profileOpen ? "Hide asset profile" : "Show asset profile"}
          >
            <IconButton
              size="small"
              onClick={onProfileToggle}
              color={profileOpen ? "primary" : "default"}
            >
              <InfoOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Rebalance">
            <IconButton size="small" onClick={onRebalanceOpen}>
              <BalanceIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Account">
            <IconButton
              size="small"
              onClick={(e) => setMenuEl(e.currentTarget)}
              sx={{ ml: 0.5 }}
            >
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  fontSize: 13,
                  bgcolor: "primary.main",
                }}
              >
                K
              </Avatar>
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={menuEl}
            open={menuOpen}
            onClose={closeMenu}
            transformOrigin={{ horizontal: "right", vertical: "top" }}
            anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
            slotProps={{ paper: { sx: { minWidth: 200 } } }}
          >
            <MenuItem
              onClick={() => {
                togglePrivacy();
                closeMenu();
              }}
            >
              <ListItemIcon>
                {privacyMode ? (
                  <VisibilityOffIcon fontSize="small" />
                ) : (
                  <VisibilityIcon fontSize="small" />
                )}
              </ListItemIcon>
              <ListItemText>
                {privacyMode ? "Show values" : "Hide values"}
              </ListItemText>
            </MenuItem>
            <MenuItem
              onClick={() => {
                toggleTheme();
                closeMenu();
              }}
            >
              <ListItemIcon>
                {themeMode === "dark" ? (
                  <Brightness7Icon fontSize="small" />
                ) : (
                  <Brightness4Icon fontSize="small" />
                )}
              </ListItemIcon>
              <ListItemText>
                {themeMode === "dark" ? "Light mode" : "Dark mode"}
              </ListItemText>
            </MenuItem>
            <MenuItem
              onClick={() => {
                toggleDensity();
                closeMenu();
              }}
            >
              <ListItemIcon>
                {density === "compact" ? (
                  <DensityMediumIcon fontSize="small" />
                ) : (
                  <DensitySmallIcon fontSize="small" />
                )}
              </ListItemIcon>
              <ListItemText>
                {density === "compact" ? "Comfortable" : "Compact"}
              </ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem
              onClick={() => {
                onSettingsOpen();
                closeMenu();
              }}
            >
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
