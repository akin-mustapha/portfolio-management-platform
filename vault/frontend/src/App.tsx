import { useMemo } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { buildTheme } from './theme/theme'
import { useAppStore } from './store/useAppStore'
import AppShell from './layouts/AppShell'
import PortfolioTab from './pages/portfolio/tabs/PortfolioTab'
import PerformanceTab from './pages/portfolio/tabs/PerformanceTab'
import RiskTab from './pages/portfolio/tabs/RiskTab'
import OpportunitiesTab from './pages/portfolio/tabs/OpportunitiesTab'
import TaxTab from './pages/portfolio/tabs/TaxTab'

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
            <Route path="/performance" element={<PerformanceTab />} />
            <Route path="/risk" element={<RiskTab />} />
            <Route path="/opportunities" element={<OpportunitiesTab />} />
            <Route path="/tax" element={<TaxTab />} />
          </Route>
          <Route path="*" element={<Navigate to="/portfolio" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
