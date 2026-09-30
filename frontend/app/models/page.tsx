"use client";

import { useState, useEffect } from "react";
import { getModelMetadata } from "@/lib/api/market";
import * as T from "@/lib/api/types";
import { formatNumber } from "@/lib/utils";
import { Cpu, ShieldCheck, Activity, Target } from "lucide-react";

export default function ModelsPage() {
  const [data, setData] = useState<T.ModelMetadataResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelMetadata()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="py-20 text-center text-zinc-500 animate-pulse">Loading model intelligence...</div>;
  if (!data) return <div className="py-20 text-center text-red-400">Failed to load model metadata.</div>;

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-12 pb-16">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-4">Model Intelligence</h1>
        <p className="text-zinc-400 text-lg">
          Insights into the frozen Phase 12 machine learning architecture serving this application.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-6 opacity-10">
            <Cpu size={120} />
          </div>
          <div className="relative z-10">
            <p className="text-emerald-400 font-medium mb-1">Production Model</p>
            <h2 className="text-3xl font-bold text-white capitalize mb-4">{data.production_model.replace('_', ' ')}</h2>
            <div className="space-y-2 text-sm text-zinc-300">
              <p><span className="text-zinc-500">Methodology:</span> {data.ensemble_information.method.replace('_', ' ')}</p>
              <p><span className="text-zinc-500">Uncertainty:</span> {data.uncertainty_methodology.replace('_', ' ')}</p>
              <p><span className="text-zinc-500">Validation:</span> {data.validation_methodology.replace('_', ' ')}</p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
          <div className="flex items-center gap-2 mb-4 text-zinc-300 font-medium">
            <Target size={18} /> Performance Metrics
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/50">
              <p className="text-xs text-zinc-500 mb-1">R² Score</p>
              <p className="text-2xl font-semibold text-zinc-100">{formatNumber(data.metrics.R2, 3)}</p>
            </div>
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/50">
              <p className="text-xs text-zinc-500 mb-1">MAE</p>
              <p className="text-xl font-semibold text-zinc-100">£{(data.metrics.MAE / 1000000).toFixed(1)}M</p>
            </div>
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/50">
              <p className="text-xs text-zinc-500 mb-1">RMSE</p>
              <p className="text-xl font-semibold text-zinc-100">£{(data.metrics.RMSE / 1000000).toFixed(1)}M</p>
            </div>
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/50">
              <p className="text-xs text-zinc-500 mb-1">Median AE</p>
              <p className="text-xl font-semibold text-zinc-100">£{(data.metrics.median_absolute_error / 1000000).toFixed(1)}M</p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <h2 className="text-xl font-semibold flex items-center gap-2 border-b border-zinc-800 pb-2">
          <ShieldCheck size={20} className="text-emerald-500" />
          Model Architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <div>
            <h3 className="font-medium text-zinc-300 mb-2">Ensemble Composition</h3>
            <ul className="space-y-2 text-zinc-400">
              {Object.entries(data.ensemble_information.weights).map(([model, weight]) => (
                <li key={model} className="flex justify-between items-center p-3 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
                  <span>{model}</span>
                  <span className="font-mono text-emerald-400">{formatNumber(weight * 100, 1)}%</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-zinc-900/30 border border-zinc-800">
              <h3 className="font-medium text-zinc-300 mb-1">Training Window</h3>
              <p className="text-zinc-400">{data.training_period}</p>
            </div>
            <div className="p-4 rounded-xl bg-zinc-900/30 border border-zinc-800">
              <h3 className="font-medium text-zinc-300 mb-1">Final Holdout</h3>
              <p className="text-zinc-400">{data.final_holdout_period}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6 space-y-4">
        <h3 className="font-semibold text-zinc-100 flex items-center gap-2">
          <Activity size={18} className="text-amber-500" />
          System Limitations
        </h3>
        <ul className="list-disc pl-5 text-sm text-zinc-400 space-y-2">
          <li>The transfer market contains highly influential unobserved variables (e.g. contract length, agent fees, player sentiment).</li>
          <li>Prediction intervals represent statistical uncertainty, not guaranteed market value bounds.</li>
          <li>What-If Simulation calculates model sensitivity to isolated features and should not be strictly interpreted as causal outcomes.</li>
          <li>Historical data coverage varies deeply, particularly before 2015.</li>
        </ul>
      </div>
    </div>
  );
}
