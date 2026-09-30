import Link from "next/link";
import { ArrowRight, Database, LineChart, Users, Scale } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col gap-16 pb-16">
      <section className="pt-20 pb-12 flex flex-col items-center text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1 text-sm font-medium text-zinc-300 mb-8">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500 mr-2"></span>
          Phase 14 Production Models Active
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-zinc-100 mb-6">
          Premier League <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">
            Transfer Intelligence
          </span>
        </h1>
        <p className="text-lg text-zinc-400 mb-10 max-w-2xl leading-relaxed">
          Historical football performance → ML valuation → explainable transfer intelligence.
          A premium analytics and scouting platform powered by conformal prediction and tree-based ensembles.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            href="/players"
            className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-emerald-500 transition-colors"
          >
            Explore Players
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
          <Link
            href="/simulate"
            className="inline-flex items-center justify-center rounded-lg bg-zinc-800 px-6 py-3 text-sm font-semibold text-zinc-100 shadow-sm hover:bg-zinc-700 border border-zinc-700 transition-colors"
          >
            Open Simulator
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: "ML Valuation", desc: "Estimated transfer fee with uncertainty interval.", icon: LineChart, href: "/players" },
          { title: "Explainable AI", desc: "Understand model contributions behind each estimate.", icon: Database, href: "/methodology" },
          { title: "Player Similarity", desc: "Discover historically comparable players.", icon: Users, href: "/compare" },
          { title: "What-If Simulation", desc: "Test hypothetical player profiles against frozen models.", icon: Scale, href: "/simulate" },
        ].map((feature) => (
          <Link key={feature.title} href={feature.href} className="group relative rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 hover:bg-zinc-800/50 transition-colors">
            <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 text-emerald-400 group-hover:bg-zinc-700 group-hover:text-emerald-300 transition-colors">
              <feature.icon className="h-5 w-5" />
            </div>
            <h3 className="mb-2 font-semibold text-zinc-100">{feature.title}</h3>
            <p className="text-sm text-zinc-400 leading-relaxed">{feature.desc}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
