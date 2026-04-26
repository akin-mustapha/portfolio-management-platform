import { useCallback, useState } from "react";
import { Outlet } from "react-router-dom";
import { Box, LinearProgress } from "@mui/material";
import Navbar from "../components/organisms/Navbar";
import SettingsModal from "../components/organisms/SettingsModal";
import RebalanceDrawer from "../components/organisms/RebalanceDrawer";
import AssetProfileDrawer from "../components/organisms/AssetProfileDrawer";
import {
  PortfolioProvider,
  usePortfolioContext,
} from "../pages/portfolio/PortfolioContext";

function ShellInner({
  onSettingsOpen,
  onRebalanceOpen,
  profileOpen,
  onProfileToggle,
  onProfileOpen,
  onProfileClose,
}: {
  onSettingsOpen: () => void;
  onRebalanceOpen: () => void;
  profileOpen: boolean;
  onProfileToggle: () => void;
  onProfileOpen: (ticker: string) => void;
  onProfileClose: () => void;
}) {
  const { loading } = usePortfolioContext();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      <Navbar
        onSettingsOpen={onSettingsOpen}
        onRebalanceOpen={onRebalanceOpen}
        onProfileToggle={onProfileToggle}
        profileOpen={profileOpen}
      />

      {loading && <LinearProgress sx={{ height: 2 }} />}

      <Box sx={{ flex: 1, overflow: "auto" }}>
        <Outlet context={{ onProfileOpen }} />
      </Box>

      <AssetProfileDrawer open={profileOpen} onClose={onProfileClose} />
    </Box>
  );
}

export default function AppShell() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [rebalanceOpen, setRebalanceOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleSettingsOpen = useCallback(() => setSettingsOpen(true), []);
  const handleSettingsClose = useCallback(() => setSettingsOpen(false), []);
  const handleRebalanceOpen = useCallback(() => setRebalanceOpen(true), []);
  const handleRebalanceClose = useCallback(() => setRebalanceOpen(false), []);
  const handleProfileToggle = useCallback(() => setProfileOpen((v) => !v), []);
  const handleProfileClose = useCallback(() => setProfileOpen(false), []);
  const handleProfileOpen = useCallback((ticker: string) => {
    setProfileOpen(true);
    // ticker passed via outlet context to child pages
    void ticker;
  }, []);

  return (
    <PortfolioProvider>
      <ShellInner
        onSettingsOpen={handleSettingsOpen}
        onRebalanceOpen={handleRebalanceOpen}
        profileOpen={profileOpen}
        onProfileToggle={handleProfileToggle}
        onProfileOpen={handleProfileOpen}
        onProfileClose={handleProfileClose}
      />
      <SettingsModal open={settingsOpen} onClose={handleSettingsClose} />
      <RebalanceDrawer open={rebalanceOpen} onClose={handleRebalanceClose} />
    </PortfolioProvider>
  );
}
