"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { 
  getPlayerDetail, 
  getPlayerValuation, 
  getPlayerExplanation, 
  getSimilarPlayers 
} from "@/lib/api/players";
import * as T from "@/lib/api/types";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { ArrowLeft, Target, TrendingUp, TrendingDown, Users } from "lucide-react";
import Link from "next/link";

export default function PlayerProfilePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const [detail, setDetail] = useState<T.PlayerDetail | null>(null);
  const [valuation, setValuation] = useState<T.ValuationResponse | null>(null);
  const [explanation, setExplanation] = useState<T.ExplanationResponse | null>(null);
  const [similarity, setSimilarity] = useState<T.SimilarityResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [det, val, exp] = await Promise.all([
          getPlayerDetail(id),
          getPlayerValuation(id).catch(() => null), // might not have valuation if no features
          getPlayerExplanation(id).catch(() => null)
        ]);
        setDetail(det);
        setValuation(val);
        setExplanation(exp);
        
        if (det.seasons.length > 0) {
          const latestSeason = det.seasons[det.seasons.length - 1];
          const sim = await getSimilarPlayers(id, latestSeason, 5).catch(() => null);
          setSimilarity(sim);
        }
      } catch (e: any) {
        if (e.status === 404) setError("Player not found.");
        else setError("Failed to load player data.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <div className="py-20 text-center text-zinc-500 animate-pulse">Loading player profile...</div>;
  if (error || !detail) return <div className="py-20 text-center text-red-400">{error || "Player not found"}</div>;

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto pb-16">
      <button onClick={() => router.back()} className="inline-flex items-center text-sm text-zinc-400 hover:text-zinc-100 w-fit">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Search
      </button>

      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-zinc-800 pb-8">
        <div className="flex items-center gap-6">
          <div>
            <h1 className="text-4xl font-bold text-zinc-100 mb-2">{detail.player_name}</h1>
            <div className="flex flex-wrap gap-3 items-center text-sm text-zinc-400">
              <span className="px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800">
                {(detail.position === 'UNKNOWN' || !detail.position) ? '-' : detail.position}
              </span>
              <span>{detail.clubs.length > 0 ? detail.clubs[detail.clubs.length - 1] : "Club information unavailable"}</span>
              <span className="w-1 h-1 rounded-full bg-zinc-700" />
              <span>{detail.seasons[detail.seasons.length - 1]}</span>
              {detail.nationality && (
                <>
                  <span className="w-1 h-1 rounded-full bg-zinc-700" />
                  <span>{detail.nationality}</span>
                </>
              )}
              {detail.date_of_birth && (
                <>
                  <span className="w-1 h-1 rounded-full bg-zinc-700" />
                  <span>{new Date(detail.date_of_birth).toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* VALUATION HERO */}
      {valuation ? (
        <section className="rounded-2xl border border-zinc-800 bg-gradient-to-br from-zinc-900/80 to-zinc-950 p-8">
          <div className="flex flex-col md:flex-row justify-between items-start gap-8">
            <div className="flex-1">
              <p className="text-sm font-medium text-emerald-400 mb-2">Model Estimate</p>
              <div className="text-5xl font-bold tracking-tight text-white mb-2">
                {formatCurrency(valuation.prediction)}
              </div>
              <p className="text-sm text-zinc-400 mb-8">
                Prediction Interval: <span className="text-zinc-300 font-medium">{formatCurrency(valuation.lower_bound)} — {formatCurrency(valuation.upper_bound)}</span>
              </p>

              {/* HORIZONTAL RANGE VISUALIZATION */}
              <div className="relative h-12 w-full max-w-lg mt-8">
                {/* Track */}
                <div className="absolute top-1/2 left-0 w-full h-1 bg-zinc-800 -translate-y-1/2 rounded-full" />
                
                {/* Interval Area */}
                <div 
                  className="absolute top-1/2 h-1 bg-emerald-900/50 -translate-y-1/2 rounded-full"
                  style={{ 
                    left: '10%', // simplify visual representation or calculate accurately if max scale known
                    width: '80%'
                  }}
                />
                
                {/* Points */}
                <div className="absolute top-1/2 left-[10%] h-3 w-[2px] bg-zinc-500 -translate-y-1/2" />
                <div className="absolute top-1/2 right-[10%] h-3 w-[2px] bg-zinc-500 -translate-y-1/2" />
                <div className="absolute top-1/2 left-1/2 h-4 w-4 bg-emerald-500 rounded-full border-4 border-zinc-950 -translate-y-1/2 -translate-x-1/2 shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
                
                {/* Labels */}
                <div className="absolute top-full left-[10%] -translate-x-1/2 mt-2 text-xs text-zinc-500">{formatCurrency(valuation.lower_bound)}</div>
                <div className="absolute top-full right-[10%] translate-x-1/2 mt-2 text-xs text-zinc-500">{formatCurrency(valuation.upper_bound)}</div>
              </div>
            </div>
            
            <div className="flex-shrink-0 bg-zinc-900 border border-zinc-800 rounded-xl p-5 text-sm space-y-3 min-w-[250px]">
              <div className="flex justify-between border-b border-zinc-800 pb-2">
                <span className="text-zinc-500">Method</span>
                <span className="font-medium text-zinc-300 capitalize">{valuation.uncertainty_method.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-800 pb-2">
                <span className="text-zinc-500">Model</span>
                <span className="font-medium text-zinc-300 capitalize">{valuation.model.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Feature Coverage</span>
                <span className="font-medium text-zinc-300">{(valuation.feature_coverage || 0) * 100}%</span>
              </div>
            </div>
          </div>
        </section>
      ) : (
        <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-8 text-center text-zinc-500">
          Valuation data not available for this player.
        </section>
      )}

      {/* EXPLANATION */}
      {explanation && (
        <section>
          <h2 className="text-xl font-semibold mb-4">Why does the model estimate this?</h2>
          <p className="text-sm text-zinc-400 mb-6 max-w-2xl">
            These are model contributions, not causal effects. They represent how much each feature pushes the final valuation relative to the baseline.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">
              <div className="flex items-center gap-2 text-emerald-400 font-medium mb-4">
                <TrendingUp size={18} /> Positive Contributors
              </div>
              <div className="space-y-3">
                {explanation.positive_contributors.map((c, i) => (
                  <div key={i} className="flex justify-between items-center text-sm border-b border-zinc-800/50 pb-2 last:border-0">
                    <span className="text-zinc-300">{c.feature}</span>
                    <span className="text-zinc-500 text-xs uppercase">{c.impact}</span>
                  </div>
                ))}
                {explanation.positive_contributors.length === 0 && <div className="text-sm text-zinc-600">None detected</div>}
              </div>
            </div>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">
              <div className="flex items-center gap-2 text-red-400 font-medium mb-4">
                <TrendingDown size={18} /> Negative Contributors
              </div>
              <div className="space-y-3">
                {explanation.negative_contributors.map((c, i) => (
                  <div key={i} className="flex justify-between items-center text-sm border-b border-zinc-800/50 pb-2 last:border-0">
                    <span className="text-zinc-300">{c.feature}</span>
                    <span className="text-zinc-500 text-xs uppercase">{c.impact}</span>
                  </div>
                ))}
                {explanation.negative_contributors.length === 0 && <div className="text-sm text-zinc-600">None detected</div>}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* SIMILAR PLAYERS */}
      {similarity && similarity.results.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-6">
            <Users size={20} className="text-zinc-400" />
            <h2 className="text-xl font-semibold">Comparable Players</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {similarity.results.map((sim) => (
              <Link key={sim.player_id} href={`/players/${sim.player_id}`} className="group rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 hover:bg-zinc-800/60 transition-colors">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-medium text-zinc-100 group-hover:text-emerald-400 transition-colors">{sim.player_name}</h3>
                  <span className="text-xs font-semibold bg-zinc-800 text-zinc-300 px-2 py-1 rounded">{(sim.similarity_score * 100).toFixed(0)}%</span>
                </div>
                <div className="space-y-1 text-sm text-zinc-400">
                  <p>{sim.position} &middot; {sim.season}</p>
                  <p>Fee: {sim.historical_transfer_fee ? formatCurrency(sim.historical_transfer_fee) : "Unknown"}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
      
      {/* TRANSFER HISTORY */}
      {detail.transfer_history && detail.transfer_history.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold mb-6">Transfer History</h2>
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-900 border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3 text-zinc-400 font-medium">Season</th>
                  <th className="px-4 py-3 text-zinc-400 font-medium">Type</th>
                  <th className="px-4 py-3 text-zinc-400 font-medium">From</th>
                  <th className="px-4 py-3 text-zinc-400 font-medium">To</th>
                  <th className="px-4 py-3 text-zinc-400 font-medium text-right">Fee</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {detail.transfer_history.map((tx, i) => (
                  <tr key={i} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 text-zinc-300">{tx.season_id}</td>
                    <td className="px-4 py-3 text-zinc-300">{tx.transfer_type}</td>
                    <td className="px-4 py-3 text-zinc-300">{tx.seller_club}</td>
                    <td className="px-4 py-3 text-zinc-300">{tx.buyer_club}</td>
                    <td className="px-4 py-3 font-medium text-right text-emerald-400">
                      {tx.fee_gbp ? formatCurrency(tx.fee_gbp) : 'Undisclosed / Free'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

    </div>
  );
}
