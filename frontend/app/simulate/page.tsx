"use client";

import { useState, useEffect } from "react";
import { searchPlayers, getPlayerDetail, getPlayerValuation } from "@/lib/api/players";
import { simulateWhatIf } from "@/lib/api/simulation";
import * as T from "@/lib/api/types";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { Search, AlertTriangle, ArrowRight, Settings2 } from "lucide-react";

export default function SimulatePage() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 500);
  const [searchResults, setSearchResults] = useState<T.PlayerSearchItem[]>([]);
  
  const [selectedPlayer, setSelectedPlayer] = useState<T.PlayerDetail | null>(null);
  const [baseline, setBaseline] = useState<T.ValuationResponse | null>(null);
  
  // The scenario inputs
  const [changes, setChanges] = useState<Record<string, number>>({});
  
  const [simulation, setSimulation] = useState<T.SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [simLoading, setSimLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!debouncedQuery) {
      setSearchResults([]);
      return;
    }
    searchPlayers(debouncedQuery, undefined, undefined, 5)
      .then(res => setSearchResults(res.items))
      .catch(() => setSearchResults([]));
  }, [debouncedQuery]);

  async function handleSelectPlayer(id: string) {
    try {
      setLoading(true);
      setError("");
      setQuery("");
      setSearchResults([]);
      const [detail, val] = await Promise.all([
        getPlayerDetail(id),
        getPlayerValuation(id).catch(() => null)
      ]);
      setSelectedPlayer(detail);
      setBaseline(val);
      setChanges({});
      setSimulation(null);
      if (!val) setError("No baseline valuation available for this player to simulate against.");
    } catch (e) {
      setError("Failed to load player.");
    } finally {
      setLoading(false);
    }
  }

  async function runSimulation() {
    if (!selectedPlayer || !baseline) return;
    try {
      setSimLoading(true);
      setError("");
      const latestSeason = selectedPlayer.seasons[selectedPlayer.seasons.length - 1];
      const res = await simulateWhatIf(selectedPlayer.player_id, latestSeason, changes);
      setSimulation(res);
    } catch (e: any) {
      setError(e.data?.detail || "Simulation failed.");
    } finally {
      setSimLoading(false);
    }
  }

  const handleSliderChange = (feature: string, value: number) => {
    setChanges(prev => ({ ...prev, [feature]: value }));
  };

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">What-If Simulator</h1>
        <p className="text-zinc-400 max-w-2xl">
          Test hypothetical player profiles against the frozen production model to observe valuation sensitivity.
          Scenario estimates represent model sensitivity, not causal predictions.
        </p>
      </div>

      {!selectedPlayer && (
        <div className="max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 h-5 w-5" />
            <input
              type="text"
              placeholder="Search for a player to simulate..."
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-zinc-100 placeholder:text-zinc-500"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          {searchResults.length > 0 && (
            <div className="mt-2 border border-zinc-800 bg-zinc-900 rounded-lg overflow-hidden">
              {searchResults.map(p => (
                <button
                  key={p.player_id}
                  onClick={() => handleSelectPlayer(p.player_id)}
                  className="w-full text-left px-4 py-3 hover:bg-zinc-800 transition-colors border-b border-zinc-800 last:border-0 text-sm"
                >
                  <span className="font-medium text-zinc-200">{p.player_name}</span>
                  <span className="text-zinc-500 ml-2">({p.position})</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {loading && <div className="text-zinc-500 animate-pulse">Loading player data...</div>}
      {error && <div className="text-red-400 p-4 bg-red-500/10 rounded-lg border border-red-500/20">{error}</div>}

      {selectedPlayer && baseline && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* LEFT: CONTROLS */}
          <div className="lg:col-span-1 space-y-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-semibold text-zinc-100">{selectedPlayer.player_name}</h2>
                <p className="text-sm text-zinc-400">{selectedPlayer.position} &middot; {selectedPlayer.seasons[selectedPlayer.seasons.length - 1]}</p>
              </div>
              <button onClick={() => setSelectedPlayer(null)} className="text-xs text-emerald-500 hover:text-emerald-400 underline">Change</button>
            </div>

            <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4 text-sm font-medium text-zinc-300">
                <Settings2 size={16} /> Scenario Controls
              </div>
              
              <div className="space-y-6">
                {[
                  { id: "t1_goals_per90", label: "Goals / 90", min: 0, max: 2, step: 0.05, defaultVal: 0 },
                  { id: "t1_assists_per90", label: "Assists / 90", min: 0, max: 2, step: 0.05, defaultVal: 0 },
                  { id: "t1_minutes", label: "Minutes", min: 0, max: 3500, step: 100, defaultVal: 1500 },
                  { id: "t1_bps_per90", label: "BPS / 90", min: 0, max: 30, step: 0.5, defaultVal: 10 },
                ].map(ctrl => {
                  const val = changes[ctrl.id] !== undefined ? changes[ctrl.id] : ctrl.defaultVal;
                  return (
                    <div key={ctrl.id}>
                      <div className="flex justify-between text-xs mb-2">
                        <label className="text-zinc-400">{ctrl.label}</label>
                        <span className="text-emerald-400 font-medium">{val}</span>
                      </div>
                      <input 
                        type="range" 
                        min={ctrl.min} max={ctrl.max} step={ctrl.step}
                        value={val}
                        onChange={(e) => handleSliderChange(ctrl.id, parseFloat(e.target.value))}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                  );
                })}
              </div>

              <button 
                onClick={runSimulation}
                disabled={simLoading}
                className="w-full mt-8 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50"
              >
                {simLoading ? "Simulating..." : "Run Simulation"}
              </button>
            </div>
          </div>

          {/* RIGHT: RESULTS */}
          <div className="lg:col-span-2 space-y-6">
            {!simulation ? (
              <div className="h-full border border-dashed border-zinc-800 rounded-xl flex items-center justify-center p-12 text-zinc-500 bg-zinc-900/20">
                Adjust controls and run simulation to see what-if outcomes.
              </div>
            ) : (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                
                {/* DELTA CARD */}
                <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
                    <div>
                      <p className="text-sm font-medium text-zinc-500 mb-1 uppercase tracking-wider">Baseline</p>
                      <p className="text-3xl font-semibold text-zinc-300">{formatCurrency(simulation.baseline.prediction)}</p>
                    </div>
                    <div className="hidden md:flex items-center justify-center text-zinc-700">
                      <ArrowRight size={32} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-zinc-500 mb-1 uppercase tracking-wider">Scenario</p>
                      <p className="text-3xl font-semibold text-emerald-400">{formatCurrency(simulation.scenario.prediction)}</p>
                    </div>
                  </div>

                  <div className="mt-8 pt-8 border-t border-zinc-800 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div>
                      <p className="text-sm text-zinc-400">Estimated Change</p>
                      <p className={`text-2xl font-bold ${simulation.absolute_change >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                        {simulation.absolute_change >= 0 ? '+' : ''}{formatCurrency(simulation.absolute_change)}
                        <span className="text-sm ml-2 font-medium opacity-80">
                          ({simulation.percentage_change > 0 ? '+' : ''}{simulation.percentage_change.toFixed(1)}%)
                        </span>
                      </p>
                    </div>

                    <div className="text-xs text-zinc-500 space-y-1 text-right">
                      <p>Baseline interval: {formatCurrency(simulation.baseline.lower_bound)} — {formatCurrency(simulation.baseline.upper_bound)}</p>
                      <p>Scenario interval: {formatCurrency(simulation.scenario.lower_bound)} — {formatCurrency(simulation.scenario.upper_bound)}</p>
                    </div>
                  </div>
                </div>

                {/* WARNINGS */}
                {simulation.warnings && simulation.warnings.length > 0 && (
                  <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 flex gap-3 text-yellow-200/80">
                    <AlertTriangle className="shrink-0 h-5 w-5 text-yellow-500/70" />
                    <div className="text-sm space-y-1">
                      <p className="font-medium text-yellow-500/90">Out of Distribution</p>
                      <ul className="list-disc pl-4 opacity-80">
                        {simulation.warnings.map((w, i) => <li key={i}>{w}</li>)}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
