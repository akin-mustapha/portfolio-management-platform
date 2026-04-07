import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material'
import Brightness4Icon from '@mui/icons-material/Brightness4'
import Brightness7Icon from '@mui/icons-material/Brightness7'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import SettingsIcon from '@mui/icons-material/Settings'
import BalanceIcon from '@mui/icons-material/Balance'
import { useAppStore } from '../../store/useAppStore'

interface NavbarProps {
  onSettingsOpen: () => void
  onRebalanceOpen: () => void
}

export default function Navbar({ onSettingsOpen, onRebalanceOpen }: NavbarProps) {
  const { themeMode, toggleTheme, privacyMode, togglePrivacy } = useAppStore()

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        color: 'text.primary',
      }}
    >
      <Toolbar variant="dense" sx={{ gap: 1 }}>
        <Typography variant="subtitle1" fontWeight={700} sx={{ flexGrow: 1 }}>
          Portfolio
        </Typography>

        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title={privacyMode ? 'Show values' : 'Hide values'}>
            <IconButton size="small" onClick={togglePrivacy}>
              {privacyMode ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Toggle theme">
            <IconButton size="small" onClick={toggleTheme}>
              {themeMode === 'dark' ? (
                <Brightness7Icon fontSize="small" />
              ) : (
                <Brightness4Icon fontSize="small" />
              )}
            </IconButton>
          </Tooltip>

          <Tooltip title="Rebalance">
            <IconButton size="small" onClick={onRebalanceOpen}>
              <BalanceIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Settings">
            <IconButton size="small" onClick={onSettingsOpen}>
              <SettingsIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  )
}
