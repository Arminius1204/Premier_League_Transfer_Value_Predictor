"use client";

import { useState, useEffect } from "react";
import { getTransfers } from "@/lib/api/transfers";
import * as T from "@/lib/api/types";
import { formatCurrency } from "@/lib/utils";
import { ChevronLeft, ChevronRight, Filter } from "lucide-react";

export default function TransfersPage() {
  const [data, setData] = useState<T.TransferResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [season, setSeason] = useState("");
  const limit = 30;

  useEffect(() => {
    setLoading(true);
    getTransfers({ season, limit, offset: page * limit })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [season, page]);

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-16">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Transfer Market Explorer</h1>
        <p className="text-zinc-400">Browse historical canonical transfer records.</p>
      </div>

      <div className="flex items-center gap-4 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
        <Filter size={18} className="text-zinc-500" />
        <select
          className="bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500 text-zinc-100"
          value={season}
          onChange={(e) => { setSeason(e.target.value); setPage(0); }}
        >
          <option value="">All Seasons</option>
          <option value="2023-2024">2023-2024</option>
          <option value="2022-2023">2022-2023</option>
          <option value="2021-2022">2021-2022</option>
          <option value="2020-2021">2020-2021</option>
        </select>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-zinc-500 animate-pulse">Loading transfers...</div>
        ) : data?.items.length === 0 ? (
          <div className="p-12 text-center text-zinc-500">No transfers found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-zinc-900/80 border-b border-zinc-800">
                <tr>
                  <th className="px-6 py-4 font-medium text-zinc-400">Player</th>
                  <th className="px-6 py-4 font-medium text-zinc-400">Season</th>
                  <th className="px-6 py-4 font-medium text-zinc-400">Type</th>
                  <th className="px-6 py-4 font-medium text-zinc-400">From</th>
                  <th className="px-6 py-4 font-medium text-zinc-400">To</th>
                  <th className="px-6 py-4 font-medium text-zinc-400 text-right">Fee</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/50">
                {data?.items.map((tx, i) => (
                  <tr key={i} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-zinc-200">{tx.player_name || tx.player_id}</td>
                    <td className="px-6 py-4 text-zinc-400">{tx.season_id}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        tx.transfer_type === 'Purchase' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                        tx.transfer_type === 'Loan' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                        tx.transfer_type === 'Free Transfer' ? 'bg-zinc-500/10 text-zinc-300 border-zinc-500/20' :
                        'bg-zinc-800 text-zinc-400 border-zinc-700'
                      }`}>
                        {tx.transfer_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-zinc-300">{tx.seller_club}</td>
                    <td className="px-6 py-4 text-zinc-300">{tx.buyer_club}</td>
                    <td className="px-6 py-4 text-right font-medium text-zinc-100">
                      {tx.fee_gbp ? formatCurrency(tx.fee_gbp) : <span className="text-zinc-500 text-xs uppercase tracking-wider">Undisclosed</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {data && data.total > limit && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-zinc-500">
            Showing {data.offset + 1} to {Math.min(data.offset + limit, data.total)} of {data.total}
          </p>
          <div className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              className="p-2 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              disabled={data.offset + limit >= data.total}
              onClick={() => setPage(p => p + 1)}
              className="p-2 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
