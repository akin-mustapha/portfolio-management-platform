import { createTheme, type PaletteMode } from '@mui/material'
import { lightTokens, darkTokens } from './tokens'

export function buildTheme(mode: PaletteMode) {
  const t = mode === 'dark' ? darkTokens : lightTokens

  return createTheme({
    palette: {
      mode,
      primary: { main: t.primary },
      success: { main: t.positive },
      error: { main: t.negative },
      background: {
        default: t.bgApp,
        paper: t.bgCard,
      },
      text: {
        primary: t.textPrimary,
        secondary: t.textSecondary,
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
      fontSize: 13,
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: t.bgApp,
            color: t.textPrimary,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            border: `1px solid ${t.bgCardBorder}`,
            borderRadius: 8,
          },
        },
      },
      // MuiDataGrid overrides are applied via `sx` prop in the component directly
      // (the theme augmentation for DataGrid requires @mui/x-data-grid/themeAugmentation)
    },
  })
}
