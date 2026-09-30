"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { searchPlayers } from "@/lib/api/players";
import { PlayerSearchResponse, PlayerSearchItem } from "@/lib/api/types";
import { Search, ChevronLeft, ChevronRight, User } from "lucide-react";
import { useDebounce } from "@/lib/hooks/useDebounce"; // need to create this

export default function PlayersPage() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 500);
  const [position, setPosition] = useState("");
  const [data, setData] = useState<PlayerSearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    searchPlayers(debouncedQuery, undefined, position || undefined, limit, page * limit)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [debouncedQuery, position, page]);

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Player Database</h1>
        <p className="text-zinc-400">Search and explore historical player performance and valuations.</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-grow">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 h-5 w-5" />
          <input
            type="text"
            placeholder="Search players by name or ID..."
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-shadow text-zinc-100 placeholder:text-zinc-500"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setPage(0); }}
          />
        </div>
        <select
          className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-zinc-100"
          value={position}
          onChange={(e) => { setPosition(e.target.value); setPage(0); }}
        >
          <option value="">All Positions</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
          <option value="UNKNOWN">Unknown</option>
        </select>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-zinc-500">Loading players...</div>
        ) : data?.items.length === 0 ? (
          <div className="p-12 text-center text-zinc-500">No players matched your search.</div>
        ) : (
          <div className="divide-y divide-zinc-800">
            {data?.items.map((player) => (
              <Link
                key={player.player_id}
                href={`/players/${player.player_id}`}
                className="flex items-center justify-between p-4 hover:bg-zinc-800/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-400">
                    <User size={20} />
                  </div>
                  <div>
                    <h3 className="font-medium text-zinc-100">{player.player_name}</h3>
                    <p className="text-xs text-zinc-400">{player.position}</p>
                  </div>
                </div>
                <div className="text-sm font-medium text-emerald-400">
                  View Profile &rarr;
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {data && data.total > limit && (
        <div className="flex items-center justify-between border-t border-zinc-800 pt-4">
          <p className="text-sm text-zinc-400">
            Showing {data.offset + 1} to {Math.min(data.offset + limit, data.total)} of {data.total} results
          </p>
          <div className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              className="p-2 rounded-lg border border-zinc-800 hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              disabled={data.offset + limit >= data.total}
              onClick={() => setPage(p => p + 1)}
              className="p-2 rounded-lg border border-zinc-800 hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
