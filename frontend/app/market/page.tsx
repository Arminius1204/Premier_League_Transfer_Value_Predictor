"use client";

import { useState, useEffect } from "react";
import { getMarketAnalysis } from "@/lib/api/market";
import * as T from "@/lib/api/types";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { BarChart3, Database, Filter } from "lucide-react";

export default function MarketPage() {
  const [data, setData] = useState<T.MarketAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [season, setSeason] = useState("");
  const [position, setPosition] = useState("");

  useEffect(() => {
    setLoading(true);
    getMarketAnalysis(season || undefined, position || undefined)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [season, position]);

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Market Analysis</h1>
        <p className="text-zinc-400">Aggregate historical transfer market statistics.</p>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
        <Filter size={18} className="text-zinc-500 hidden sm:block" />
        <select
          className="bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500 text-zinc-100"
          value={season}
          onChange={(e) => setSeason(e.target.value)}
        >
          <option value="">All Seasons</option>
          <option value="2023-2024">2023-2024</option>
          <option value="2022-2023">2022-2023</option>
          <option value="2021-2022">2021-2022</option>
          <option value="2020-2021">2020-2021</option>
        </select>
        <select
          className="bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500 text-zinc-100"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
        >
          <option value="">All Positions</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
        </select>
      </div>

      {loading ? (
        <div className="p-20 text-center text-zinc-500 animate-pulse border border-zinc-800 rounded-xl bg-zinc-900/40">
          Loading market analysis...
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60">
            <div className="flex items-center gap-2 text-zinc-500 mb-2">
              <Database size={16} /> <span className="text-sm font-medium uppercase tracking-wider">Total Transfers</span>
            </div>
            <p className="text-4xl font-bold text-zinc-100">{formatNumber(data.total_transfers, 0)}</p>
          </div>
          
          <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60">
            <div className="flex items-center gap-2 text-zinc-500 mb-2">
              <Database size={16} /> <span className="text-sm font-medium uppercase tracking-wider">Disclosed</span>
            </div>
            <p className="text-4xl font-bold text-emerald-400">{formatNumber(data.disclosed_transfers, 0)}</p>
            <p className="text-xs text-zinc-500 mt-2">{(data.disclosed_transfers / data.total_transfers * 100).toFixed(1)}% of total</p>
          </div>

          <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60">
            <div className="flex items-center gap-2 text-zinc-500 mb-2">
              <BarChart3 size={16} /> <span className="text-sm font-medium uppercase tracking-wider">Median Fee</span>
            </div>
            <p className="text-4xl font-bold text-zinc-100">{formatCurrency(data.median_fee)}</p>
          </div>

          <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60">
            <div className="flex items-center gap-2 text-zinc-500 mb-2">
              <BarChart3 size={16} /> <span className="text-sm font-medium uppercase tracking-wider">Mean Fee</span>
            </div>
            <p className="text-4xl font-bold text-zinc-100">{formatCurrency(data.mean_fee)}</p>
          </div>
        </div>
      ) : (
        <div className="p-20 text-center text-red-400 border border-zinc-800 rounded-xl bg-zinc-900/40">
          Failed to load data.
        </div>
      )}
    </div>
  );
}
