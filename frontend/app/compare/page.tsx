"use client";

import { useState, useEffect } from "react";
import { searchPlayers, getPlayerDetail, getPlayerValuation } from "@/lib/api/players";
import * as T from "@/lib/api/types";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { Search, X, Plus } from "lucide-react";

export default function ComparePage() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 500);
  const [searchResults, setSearchResults] = useState<T.PlayerSearchItem[]>([]);
  
  const [selectedPlayers, setSelectedPlayers] = useState<{
    detail: T.PlayerDetail;
    valuation: T.ValuationResponse | null;
  }[]>([]);
  
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!debouncedQuery) {
      setSearchResults([]);
      return;
    }
    searchPlayers(debouncedQuery, undefined, undefined, 5)
      .then(res => setSearchResults(res.items))
      .catch(() => setSearchResults([]));
  }, [debouncedQuery]);

  async function handleAddPlayer(id: string) {
    if (selectedPlayers.length >= 3) return;
    if (selectedPlayers.find(p => p.detail.player_id === id)) return;
    
    try {
      setLoading(true);
      setQuery("");
      setSearchResults([]);
      const [detail, val] = await Promise.all([
        getPlayerDetail(id),
        getPlayerValuation(id).catch(() => null)
      ]);
      setSelectedPlayers(prev => [...prev, { detail, valuation: val }]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  function handleRemovePlayer(id: string) {
    setSelectedPlayers(prev => prev.filter(p => p.detail.player_id !== id));
  }

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Player Comparison</h1>
        <p className="text-zinc-400">Compare valuations and contextual profiles of up to 3 players simultaneously.</p>
      </div>

      {selectedPlayers.length < 3 && (
        <div className="max-w-xl relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 h-5 w-5" />
          <input
            type="text"
            placeholder="Search to add a player..."
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-zinc-100 placeholder:text-zinc-500"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {searchResults.length > 0 && (
            <div className="absolute z-10 w-full mt-2 border border-zinc-800 bg-zinc-900 rounded-lg overflow-hidden shadow-xl">
              {searchResults.map(p => (
                <button
                  key={p.player_id}
                  onClick={() => handleAddPlayer(p.player_id)}
                  className="w-full text-left px-4 py-3 hover:bg-zinc-800 transition-colors border-b border-zinc-800 last:border-0 text-sm flex justify-between items-center"
                >
                  <div>
                    <span className="font-medium text-zinc-200">{p.player_name}</span>
                    <span className="text-zinc-500 ml-2">({p.position})</span>
                  </div>
                  <Plus size={16} className="text-zinc-500" />
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {loading && <div className="text-zinc-500 animate-pulse">Loading player...</div>}

      {selectedPlayers.length > 0 ? (
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-4 min-w-max">
            {selectedPlayers.map((player) => (
              <div key={player.detail.player_id} className="w-80 flex-shrink-0 bg-zinc-900/40 border border-zinc-800 rounded-2xl overflow-hidden">
                <div className="p-6 border-b border-zinc-800 relative bg-zinc-900/80">
                  <button 
                    onClick={() => handleRemovePlayer(player.detail.player_id)}
                    className="absolute top-4 right-4 text-zinc-500 hover:text-red-400 bg-zinc-950 rounded-full p-1 border border-zinc-800"
                  >
                    <X size={16} />
                  </button>
                  <h2 className="text-xl font-bold text-zinc-100 pr-8">{player.detail.player_name}</h2>
                  <p className="text-sm text-zinc-400 mt-1">{player.detail.position}</p>
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Model Estimate</p>
                    {player.valuation ? (
                      <>
                        <p className="text-3xl font-bold text-emerald-400">{formatCurrency(player.valuation.prediction)}</p>
                        <p className="text-xs text-zinc-400 mt-1">
                          Range: {formatCurrency(player.valuation.lower_bound)} - {formatCurrency(player.valuation.upper_bound)}
                        </p>
                      </>
                    ) : (
                      <p className="text-sm text-zinc-500">Not available</p>
                    )}
                  </div>
                  
                  <div className="space-y-3 pt-6 border-t border-zinc-800/50">
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Clubs</p>
                      <p className="text-sm text-zinc-300">{player.detail.clubs.slice(-2).join(", ")}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Seasons</p>
                      <p className="text-sm text-zinc-300">{player.detail.seasons.slice(-2).join(", ")}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Latest Transfer</p>
                      <p className="text-sm text-zinc-300">
                        {player.detail.transfer_history && player.detail.transfer_history.length > 0 
                          ? formatCurrency(player.detail.transfer_history[player.detail.transfer_history.length - 1].fee_gbp)
                          : "No record"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {selectedPlayers.length < 3 && (
              <div className="w-80 flex-shrink-0 border border-dashed border-zinc-800 rounded-2xl flex items-center justify-center p-6 text-zinc-500 bg-zinc-900/10 h-auto">
                <div className="text-center">
                  <Plus size={24} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Add another player<br/>to compare</p>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="border border-dashed border-zinc-800 rounded-2xl flex items-center justify-center p-20 text-zinc-500 bg-zinc-900/10">
          Search and add players to begin comparison.
        </div>
      )}
    </div>
  );
}
