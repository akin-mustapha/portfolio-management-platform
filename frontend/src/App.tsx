import { useMemo } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { buildTheme } from './theme/theme'
import { useAppStore } from './store/useAppStore'
import PortfolioPage from './pages/portfolio/PortfolioPage'

export default function App() {
  const themeMode = useAppStore((s) => s.themeMode)
  const theme = useMemo(() => buildTheme(themeMode), [themeMode])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="*" element={<Navigate to="/portfolio" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
