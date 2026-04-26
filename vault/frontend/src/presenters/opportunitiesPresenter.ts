import type { PositionDistributionItem } from "./portfolioPresenter";

// ---- View models ----

export interface EnrichedPositionPoint extends PositionDistributionItem {
  fill: string;
  pointOpacity: number;
  pointStroke: string;
  pointStrokeWidth: number;
  bubbleRadius: number;
}

export interface PerformanceMapVM {
  enrichedData: EnrichedPositionPoint[];
  xDomain: [number, number];
  yDomain: [number, number];
  medianWeight: number;
  allEqualWeight: boolean;
}

export interface OpportunitiesChartVM {
  distribution: PositionDistributionItem[];
  avgWeight: number;
}

// ---- Helpers (pure) ----

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

const R_MIN = 4;
const R_MAX = 14;

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

// ---- Presenter functions ----

export function presentPerformanceMap(
  distribution: PositionDistributionItem[],
  selectedTickers: string[],
): PerformanceMapVM | null {
  if (!distribution.length) return null;

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

  const xDomain: [number, number] = [xMin - xPad, xMax + xPad];
  const yDomain: [number, number] = [0, yMax + yPad];
  const allEqualWeight = medianWeight === yMax;

  const hasSelection = selectedTickers.length > 0;
  const enrichedData: EnrichedPositionPoint[] = distribution.map((d) => ({
    ...d,
    fill: interpolateColor(d.value, valueMin, valueMax, COLOR_STOPS),
    pointOpacity:
      hasSelection && !selectedTickers.includes(d.ticker) ? 0.15 : 1.0,
    pointStroke: selectedTickers.includes(d.ticker) ? "#ffffff" : "none",
    pointStrokeWidth: selectedTickers.includes(d.ticker) ? 2 : 0,
    bubbleRadius: scaleBubble(d.weight_pct, weightMin, yMax),
  }));

  return { enrichedData, xDomain, yDomain, medianWeight, allEqualWeight };
}

export function presentOpportunitiesChart(
  distribution: PositionDistributionItem[],
): OpportunitiesChartVM {
  const avgWeight = distribution.length
    ? distribution.reduce((s, d) => s + d.weight_pct, 0) / distribution.length
    : 0;
  return { distribution, avgWeight };
}
