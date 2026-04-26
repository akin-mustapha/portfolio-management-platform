import { useMemo } from "react";
import { useTheme, Paper, Typography } from "@mui/material";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
  CartesianGrid,
} from "recharts";

interface PositionDistributionPoint {
  ticker: string;
  name: string;
  weight_pct: number;
  roi_pct: number;
  profit: number;
  value: number;
}

interface EnrichedPoint extends PositionDistributionPoint {
  fill: string;
  pointOpacity: number;
  pointStroke: string;
  pointStrokeWidth: number;
  bubbleRadius: number;
}

interface PositionPerformanceMapProps {
  distribution?: PositionDistributionPoint[];
  currencySymbol?: string;
  selectedTickers?: string[];
}

const COLOR_STOPS = ["#3d0173", "#8b1a6b", "#d4515a", "#f4a247", "#f5e96a"];

function hexToRgb(hex: string): [number, number, number] {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function interpolateColor(
  value: number,
  min: number,
  max: number,
  stops: string[],
): string {
  const t =
    max === min ? 0.5 : Math.max(0, Math.min(1, (value - min) / (max - min)));
  const scaled = t * (stops.length - 1);
  const lo = Math.floor(scaled);
  const hi = Math.min(stops.length - 1, lo + 1);
  const frac = scaled - lo;
  const [r1, g1, b1] = hexToRgb(stops[lo]);
  const [r2, g2, b2] = hexToRgb(stops[hi]);
  return `rgb(${Math.round(r1 + (r2 - r1) * frac)},${Math.round(g1 + (g2 - g1) * frac)},${Math.round(b1 + (b2 - b1) * frac)})`;
}

const R_MIN = 4; // px — minimum always-visible radius
const R_MAX = 14; // px — maximum radius (28px diameter)

// sqrt scaling so bubble area ∝ weight_pct (perceptually accurate)
function scaleBubble(w: number, wMin: number, wMax: number): number {
  if (wMax === wMin) return (R_MIN + R_MAX) / 2;
  const t = (w - wMin) / (wMax - wMin);
  return R_MIN + Math.sqrt(t) * (R_MAX - R_MIN);
}

function computeMedian(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0
    ? sorted[mid]
    : (sorted[mid - 1] + sorted[mid]) / 2;
}

function CustomTooltip({
  active,
  payload,
  currencySymbol,
}: {
  active?: boolean;
  payload?: Array<{ payload: EnrichedPoint }>;
  currencySymbol?: string;
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  const sym = currencySymbol ?? "";
  return (
    <Paper sx={{ p: 1.5, fontSize: 11, minWidth: 140 }}>
      <Typography variant="caption" fontWeight={700} display="block">
        {d.ticker}
      </Typography>
      <Typography
        variant="caption"
        color="text.secondary"
        display="block"
        sx={{ mb: 0.5 }}
      >
        {d.name}
      </Typography>
      <Typography variant="caption" display="block">
        ROI: {d.roi_pct.toFixed(2)}%
      </Typography>
      <Typography variant="caption" display="block">
        Return: {sym}
        {d.profit.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </Typography>
      <Typography variant="caption" display="block">
        Weight: {d.weight_pct.toFixed(2)}%
      </Typography>
      <Typography variant="caption" display="block">
        Value: {sym}
        {d.value.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </Typography>
    </Paper>
  );
}

// Defined outside component so the reference is stable across renders
function BubbleShape(props: Record<string, unknown>) {
  const cx = props.cx as number;
  const cy = props.cy as number;
  const payload = props.payload as EnrichedPoint;
  const r = payload?.bubbleRadius ?? 6;
  if (!payload || cx == null || cy == null) return null;
  return (
    <circle
      cx={cx}
      cy={cy}
      r={r}
      fill={payload.fill}
      opacity={payload.pointOpacity}
      stroke={payload.pointStroke}
      strokeWidth={payload.pointStrokeWidth}
    />
  );
}

export default function PositionPerformanceMap({
  distribution,
  currencySymbol,
  selectedTickers = [],
}: PositionPerformanceMapProps) {
  const theme = useTheme();

  const derived = useMemo(() => {
    if (!distribution?.length) return null;
    const roiValues = distribution.map((d) => d.roi_pct);
    const weightValues = distribution.map((d) => d.weight_pct);
    const posValues = distribution.map((d) => d.value);
    const xMin = Math.min(...roiValues);
    const xMax = Math.max(...roiValues);
    const yMax = Math.max(...weightValues);
    const weightMin = Math.min(...weightValues);
    const valueMin = Math.min(...posValues);
    const valueMax = Math.max(...posValues);
    const medianWeight = computeMedian(weightValues);
    const xPad = (xMax - xMin) * 0.08 || 1;
    const yPad = yMax * 0.08 || 0.5;
    return {
      xDomain: [xMin - xPad, xMax + xPad] as [number, number],
      yDomain: [0, yMax + yPad] as [number, number],
      valueMin,
      valueMax,
      weightMin,
      weightMax: yMax,
      medianWeight,
      allEqualWeight: medianWeight === yMax,
    };
  }, [distribution]);

  // Pre-compute visual properties so the shape renderer is a stable module-level function
  const enrichedData = useMemo<EnrichedPoint[]>(() => {
    if (!distribution?.length || !derived) return [];
    const { valueMin, valueMax, weightMin, weightMax } = derived;
    const hasSelection = selectedTickers.length > 0;
    return distribution.map((d) => ({
      ...d,
      fill: interpolateColor(d.value, valueMin, valueMax, COLOR_STOPS),
      pointOpacity:
        hasSelection && !selectedTickers.includes(d.ticker) ? 0.15 : 1.0,
      pointStroke: selectedTickers.includes(d.ticker) ? "#ffffff" : "none",
      pointStrokeWidth: selectedTickers.includes(d.ticker) ? 2 : 0,
      bubbleRadius: scaleBubble(d.weight_pct, weightMin, weightMax),
    }));
  }, [distribution, derived, selectedTickers]);

  if (!derived || !enrichedData.length) return null;

  const { xDomain, yDomain, medianWeight, allEqualWeight } = derived;
  const quadrantLabel = { fontSize: 9, fill: theme.palette.text.disabled };

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ScatterChart margin={{ top: 20, right: 24, bottom: 28, left: 0 }}>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={theme.palette.divider}
          opacity={0.4}
        />
        <XAxis
          dataKey="roi_pct"
          type="number"
          name="ROI %"
          domain={xDomain}
          tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
          tick={{ fontSize: 10, fill: theme.palette.text.secondary }}
          tickLine={false}
          axisLine={{ stroke: theme.palette.divider }}
          label={{
            value: "ROI %",
            position: "insideBottom",
            offset: -12,
            fill: theme.palette.text.secondary,
            fontSize: 10,
          }}
        />
        <YAxis
          dataKey="weight_pct"
          type="number"
          name="Weight %"
          domain={yDomain}
          tickFormatter={(v) => `${Number(v).toFixed(1)}%`}
          tick={{ fontSize: 10, fill: theme.palette.text.secondary }}
          tickLine={false}
          axisLine={{ stroke: theme.palette.divider }}
          width={44}
          label={{
            value: "Weight %",
            angle: -90,
            position: "insideLeft",
            offset: 10,
            fill: theme.palette.text.secondary,
            fontSize: 10,
          }}
        />
        <ZAxis range={[1, 1]} />
        <Tooltip
          content={(props) => (
            <CustomTooltip
              active={props.active}
              payload={
                props.payload as unknown as Array<{ payload: EnrichedPoint }>
              }
              currencySymbol={currencySymbol}
            />
          )}
        />

        {/* Break-even vertical line */}
        <ReferenceLine
          x={0}
          stroke={theme.palette.error.main}
          strokeWidth={1}
          strokeDasharray="4 2"
        />

        {/* Median weight horizontal line */}
        {!allEqualWeight && (
          <ReferenceLine
            y={medianWeight}
            stroke="rgba(255,220,0,0.65)"
            strokeWidth={1}
            strokeDasharray="4 2"
          />
        )}

        {/* Quadrant backgrounds + labels */}
        {!allEqualWeight && (
          <>
            <ReferenceArea
              x1={0}
              x2={xDomain[1]}
              y1={medianWeight}
              y2={yDomain[1]}
              fill={theme.palette.success.main}
              fillOpacity={0.04}
              label={{
                value: "High Value Winners",
                position: "insideTopRight",
                ...quadrantLabel,
              }}
            />
            <ReferenceArea
              x1={0}
              x2={xDomain[1]}
              y1={0}
              y2={medianWeight}
              fill={theme.palette.success.main}
              fillOpacity={0.03}
              label={{
                value: "Low Value Winners",
                position: "insideBottomRight",
                ...quadrantLabel,
              }}
            />
            <ReferenceArea
              x1={xDomain[0]}
              x2={0}
              y1={medianWeight}
              y2={yDomain[1]}
              fill={theme.palette.error.main}
              fillOpacity={0.04}
              label={{
                value: "Dead Weights",
                position: "insideTopLeft",
                ...quadrantLabel,
              }}
            />
            <ReferenceArea
              x1={xDomain[0]}
              x2={0}
              y1={0}
              y2={medianWeight}
              fill={theme.palette.warning.main}
              fillOpacity={0.03}
              label={{
                value: "Speculative",
                position: "insideBottomLeft",
                ...quadrantLabel,
              }}
            />
          </>
        )}

        <Scatter data={enrichedData} shape={BubbleShape as never} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
