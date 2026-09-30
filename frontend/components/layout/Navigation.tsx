"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchApi } from "@/lib/api/client";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { name: "Overview", href: "/" },
  { name: "Players", href: "/players" },
  { name: "Compare", href: "/compare" },
  { name: "Simulate", href: "/simulate" },
  { name: "Transfers", href: "/transfers" },
  { name: "Market", href: "/market" },
  { name: "Models", href: "/models" },
  { name: "Methodology", href: "/methodology" },
];

export default function Navigation() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    fetchApi('/health')
      .then((res: any) => setIsApiHealthy(res.status === 'ok'))
      .catch(() => setIsApiHealthy(false));
  }, []);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
                <Activity size={20} />
              </div>
              <span className="font-semibold tracking-tight text-zinc-100 hidden sm:block">
                Transfer Intelligence
              </span>
            </Link>
            <div className="hidden md:flex gap-6">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "text-sm font-medium transition-colors hover:text-zinc-100",
                    pathname === link.href ? "text-zinc-100" : "text-zinc-400"
                  )}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-zinc-500 bg-zinc-900/50 px-3 py-1.5 rounded-full border border-zinc-800">
              <span className="relative flex h-2 w-2">
                {isApiHealthy && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                <span className={cn("relative inline-flex rounded-full h-2 w-2", isApiHealthy ? "bg-emerald-500" : isApiHealthy === false ? "bg-red-500" : "bg-zinc-500")}></span>
              </span>
              API Status
            </div>
            
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 text-zinc-400 hover:text-zinc-100"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden border-b border-zinc-800 bg-zinc-950 px-4 py-4">
          <div className="flex flex-col gap-4">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-zinc-100",
                  pathname === link.href ? "text-zinc-100" : "text-zinc-400"
                )}
              >
                {link.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
