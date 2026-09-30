import { ShieldCheck, Server, BrainCircuit, Activity } from "lucide-react";

export default function MethodologyPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-12 pb-16">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-4">Methodology</h1>
        <p className="text-zinc-400 text-lg">
          Technical overview of the Premier League Transfer Intelligence platform.
        </p>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-8">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
          <Server className="text-emerald-500" /> System Pipeline
        </h2>
        
        <div className="flex flex-col gap-2 font-mono text-sm pl-4 border-l-2 border-zinc-800">
          <div className="flex items-center gap-4"><span className="text-zinc-500">01</span> <span className="text-zinc-300">Historical Data Ingestion</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">02</span> <span className="text-zinc-300">Entity Resolution (Fuzzy Matching)</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">03</span> <span className="text-emerald-400">Temporal Feature Engineering</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">04</span> <span className="text-zinc-300">Phase 12 Walk-Forward Validation</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">05</span> <span className="text-emerald-400">Tree-Based Ensemble Training</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">06</span> <span className="text-cyan-400">Conformal Prediction Intervals</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">07</span> <span className="text-emerald-400">Phase 13 Similarity & Simulation Engine</span></div>
          <div className="h-4 border-l border-dashed border-zinc-700 ml-2"></div>
          <div className="flex items-center gap-4"><span className="text-zinc-500">08</span> <span className="text-zinc-100 font-semibold">FastAPI & Next.js Analytics Platform</span></div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2"><BrainCircuit size={18} className="text-zinc-400" /> Machine Learning</h3>
          <p className="text-zinc-400 text-sm leading-relaxed mb-4">
            The valuation core utilizes a weighted ensemble of Random Forest, XGBoost, and Ridge Regression models. Features are strictly computed using information available <em>prior</em> to a transfer event to prevent temporal data leakage.
          </p>
        </section>

        <section>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2"><ShieldCheck size={18} className="text-zinc-400" /> Conformal Prediction</h3>
          <p className="text-zinc-400 text-sm leading-relaxed mb-4">
            Unlike standard regression which outputs a single point estimate, this system uses conformal prediction to generate statistically rigorous lower and upper bounds, quantifying the model's confidence in unseen data.
          </p>
        </section>

        <section>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2"><Activity size={18} className="text-zinc-400" /> Explainability</h3>
          <p className="text-zinc-400 text-sm leading-relaxed mb-4">
            Feature contributions are extracted dynamically, highlighting which metrics pushed the valuation up or down relative to the baseline. These are model sensitivities, not guaranteed causal laws of the market.
          </p>
        </section>
      </div>
    </div>
  );
}
