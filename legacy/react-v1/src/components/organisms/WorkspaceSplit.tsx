import { Group, Panel, Separator } from "react-resizable-panels";
import { Box, useTheme } from "@mui/material";
import type { ReactNode } from "react";

interface WorkspaceSplitProps {
  left: ReactNode;
  right: ReactNode;
}

export default function WorkspaceSplit({ left, right }: WorkspaceSplitProps) {
  const theme = useTheme();

  return (
    <Box sx={{ flex: 1, overflow: "hidden", display: "flex" }}>
      <Group
        orientation="horizontal"
        id="workspace-split"
        style={{ width: "100%", height: "100%", display: "flex" }}
      >
        <Panel defaultSize={55} minSize={30} id="left-panel">
          <Box
            sx={{
              height: "100%",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {left}
          </Box>
        </Panel>

        <Separator
          id="resize-handle"
          style={{
            width: 4,
            background: theme.palette.divider,
            cursor: "col-resize",
            flexShrink: 0,
          }}
        />

        <Panel defaultSize={45} minSize={25} id="right-panel">
          <Box sx={{ height: "100%", overflow: "auto" }}>{right}</Box>
        </Panel>
      </Group>
    </Box>
  );
}
