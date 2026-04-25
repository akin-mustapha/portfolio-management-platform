import { useMemo } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { buildTheme } from './theme/theme'
import { useAppStore } from './store/useAppStore'
import AppShell from './pages/portfolio/AppShell'
import PortfolioTab from './pages/portfolio/tabs/PortfolioTab'
import RiskTab from './pages/portfolio/tabs/RiskTab'
import OpportunitiesTab from './pages/portfolio/tabs/OpportunitiesTab'

export default function App() {
  const themeMode = useAppStore((s) => s.themeMode)
  const theme = useMemo(() => buildTheme(themeMode), [themeMode])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/portfolio" element={<PortfolioTab />} />
            <Route path="/risk" element={<RiskTab />} />
            <Route path="/opportunities" element={<OpportunitiesTab />} />
          </Route>
          <Route path="*" element={<Navigate to="/portfolio" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
