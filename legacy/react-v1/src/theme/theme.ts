import { createTheme, type PaletteMode } from "@mui/material";
import { lightTokens, darkTokens } from "./tokens";

declare module "@mui/material/styles" {
  interface Theme {
    custom: {
      shadowCard: string;
      shadowCardHover: string;
      bgZebra: string;
      bgRowHover: string;
      bgRowSelected: string;
    };
  }
  interface ThemeOptions {
    custom?: {
      shadowCard?: string;
      shadowCardHover?: string;
      bgZebra?: string;
      bgRowHover?: string;
      bgRowSelected?: string;
    };
  }
}

export function buildTheme(mode: PaletteMode) {
  const t = mode === "dark" ? darkTokens : lightTokens;

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
      divider: t.bgCardBorder,
    },
    shape: { borderRadius: 10 },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
      fontSize: 13,
      h6: { letterSpacing: "-0.01em", fontWeight: 700 },
      subtitle1: { letterSpacing: "-0.01em" },
      subtitle2: { letterSpacing: "-0.005em" },
      button: { textTransform: "none", fontWeight: 500 },
    },
    custom: {
      shadowCard: t.shadowCard,
      shadowCardHover: t.shadowCardHover,
      bgZebra: t.bgZebra,
      bgRowHover: t.bgRowHover,
      bgRowSelected: t.bgRowSelected,
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: t.bgApp,
            color: t.textPrimary,
            fontVariantNumeric: "tabular-nums",
          },
          "input, button, select, textarea": {
            fontFeatureSettings: '"tnum" 1',
          },
        },
      },
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            border: `1px solid ${t.bgCardBorder}`,
            borderRadius: 12,
            boxShadow: t.shadowCard,
            transition:
              "box-shadow 180ms ease, transform 180ms ease, border-color 180ms ease",
          },
        },
      },
      MuiButtonBase: {
        defaultProps: { disableRipple: false },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            fontSize: 11,
            borderRadius: 6,
          },
        },
      },
    },
  });
}
