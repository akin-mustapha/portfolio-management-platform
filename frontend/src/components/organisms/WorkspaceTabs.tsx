import { useState } from 'react'
import { Box, Tab, Tabs } from '@mui/material'
import type { ReactNode } from 'react'

interface TabDef {
  label: string
  content: ReactNode
}

interface WorkspaceTabsProps {
  tabs: TabDef[]
}

export default function WorkspaceTabs({ tabs }: WorkspaceTabsProps) {
  const [active, setActive] = useState(0)

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Tabs
        value={active}
        onChange={(_, v) => setActive(v)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ borderBottom: 1, borderColor: 'divider', minHeight: 36 }}
        TabIndicatorProps={{ style: { height: 2 } }}
      >
        {tabs.map((t, i) => (
          <Tab
            key={t.label}
            label={t.label}
            value={i}
            sx={{ minHeight: 36, fontSize: 12, textTransform: 'none', py: 0 }}
          />
        ))}
      </Tabs>

      <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        {tabs[active]?.content}
      </Box>
    </Box>
  )
}
