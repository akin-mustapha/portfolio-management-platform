import { useState } from "react";
import {
  Box,
  Button,
  Drawer,
  Slider,
  Typography,
  Alert,
  CircularProgress,
  Divider,
  Stack,
} from "@mui/material";
import {
  useRebalanceConfigs,
  useSaveRebalanceConfig,
  useGenerateRebalancePlan,
} from "../../hooks/useRebalance";
import type {
  RebalanceConfigVM,
  RebalancePlanResultVM,
} from "../../hooks/useRebalance";

interface RebalanceDrawerProps {
  open: boolean;
  onClose: () => void;
}

export default function RebalanceDrawer({
  open,
  onClose,
}: RebalanceDrawerProps) {
  const { data: configs = [], isLoading } = useRebalanceConfigs();
  const save = useSaveRebalanceConfig();
  const generate = useGenerateRebalancePlan();
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [planResult, setPlanResult] = useState<RebalancePlanResultVM | null>(
    null,
  );

  const getWeight = (c: RebalanceConfigVM) =>
    weights[c.ticker] ?? c.target_weight_pct;

  const handleSlider = (ticker: string, val: number) =>
    setWeights((prev) => ({ ...prev, [ticker]: val }));

  const handleSave = async () => {
    const pending = configs.filter((c) => weights[c.ticker] !== undefined);
    await Promise.all(
      pending.map((c) =>
        save.mutateAsync({
          asset_id: c.asset_id,
          ticker: c.ticker,
          target_weight_pct: weights[c.ticker],
          min_weight_pct: c.min_weight_pct,
          max_weight_pct: c.max_weight_pct,
        }),
      ),
    );
    setWeights({});
  };

  const handleGenerate = async () => {
    const result = await generate.mutateAsync();
    setPlanResult(result);
  };

  return (
    <Drawer
      anchor="bottom"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { maxHeight: "60vh", borderRadius: "12px 12px 0 0", p: 2 },
      }}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 1,
        }}
      >
        <Typography variant="subtitle1" fontWeight={700}>
          Rebalancing
        </Typography>
        <Button size="small" onClick={onClose}>
          Close
        </Button>
      </Box>
      <Divider sx={{ mb: 2 }} />

      {isLoading && <CircularProgress size={20} />}

      {planResult && (
        <Alert severity="info" sx={{ mb: 1, fontSize: 12 }}>
          {planResult.message}
        </Alert>
      )}

      <Box sx={{ overflowY: "auto", flex: 1 }}>
        <Stack spacing={2}>
          {configs.map((c) => {
            const target = getWeight(c);
            return (
              <Box key={c.ticker}>
                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                  <Typography variant="body2" fontWeight={600}>
                    {c.ticker}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {target.toFixed(1)}%
                  </Typography>
                </Box>
                <Slider
                  value={target}
                  min={0}
                  max={100}
                  step={0.5}
                  size="small"
                  onChange={(_, val) => handleSlider(c.ticker, val as number)}
                />
              </Box>
            );
          })}
        </Stack>
      </Box>

      <Divider sx={{ mt: 2, mb: 1 }} />
      <Box sx={{ display: "flex", gap: 1, justifyContent: "flex-end" }}>
        <Button
          size="small"
          variant="outlined"
          onClick={handleSave}
          disabled={save.isPending || Object.keys(weights).length === 0}
        >
          {save.isPending ? <CircularProgress size={14} /> : "Save Weights"}
        </Button>
        <Button
          size="small"
          variant="contained"
          onClick={handleGenerate}
          disabled={generate.isPending}
        >
          {generate.isPending ? (
            <CircularProgress size={14} />
          ) : (
            "Generate Plan"
          )}
        </Button>
      </Box>
    </Drawer>
  );
}
