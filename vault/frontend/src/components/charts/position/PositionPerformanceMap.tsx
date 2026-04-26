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
import type {
  PerformanceMapVM,
  EnrichedPositionPoint,
} from "../../../presenters/opportunitiesPresenter";

interface PositionPerformanceMapProps {
  vm?: PerformanceMapVM | null;
  currencySymbol?: string;
}

function CustomTooltip({
  active,
  payload,
  currencySymbol,
}: {
  active?: boolean;
  payload?: Array<{ payload: EnrichedPositionPoint }>;
  currencySymbol?: string;
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  const sym = currencySymbol ?? "";
  return (
    <Paper sx={{ p: 1.5, fontSize: 11, minWidth: 140 }}>
      <Typography
        variant="caption"
        sx={{ fontWeight: 700, display: "block" }}
        component="div"
      >
        {d.ticker}
      </Typography>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: "block", mb: 0.5 }}
        component="div"
      >
        {d.name}
      </Typography>
      <Typography variant="caption" sx={{ display: "block" }} component="div">
        ROI: {d.roi_pct.toFixed(2)}%
      </Typography>
      <Typography variant="caption" sx={{ display: "block" }} component="div">
        Return: {sym}
        {d.profit.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </Typography>
      <Typography variant="caption" sx={{ display: "block" }} component="div">
        Weight: {d.weight_pct.toFixed(2)}%
      </Typography>
      <Typography variant="caption" sx={{ display: "block" }} component="div">
        Value: {sym}
        {d.value.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </Typography>
    </Paper>
  );
}

function BubbleShape(props: Record<string, unknown>) {
  const cx = props.cx as number;
  const cy = props.cy as number;
  const payload = props.payload as EnrichedPositionPoint;
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
  vm,
  currencySymbol,
}: PositionPerformanceMapProps) {
  const theme = useTheme();

  if (!vm || !vm.enrichedData.length) return null;

  const { enrichedData, xDomain, yDomain, medianWeight, allEqualWeight } = vm;
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
                props.payload as unknown as Array<{
                  payload: EnrichedPositionPoint;
                }>
              }
              currencySymbol={currencySymbol}
            />
          )}
        />

        <ReferenceLine
          x={0}
          stroke={theme.palette.error.main}
          strokeWidth={1}
          strokeDasharray="4 2"
        />

        {!allEqualWeight && (
          <ReferenceLine
            y={medianWeight}
            stroke="rgba(255,220,0,0.65)"
            strokeWidth={1}
            strokeDasharray="4 2"
          />
        )}

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
