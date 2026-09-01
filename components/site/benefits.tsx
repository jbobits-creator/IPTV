import {
  Film,
  Globe2,
  Rewind,
  Ticket,
  Trophy,
  Tv,
  type LucideIcon,
} from "lucide-react"

import { BENEFITS } from "@/lib/offer"

const ICONS: Record<string, LucideIcon> = {
  tv: Tv,
  film: Film,
  trophy: Trophy,
  ticket: Ticket,
  rewind: Rewind,
  globe: Globe2,
}

export function Benefits() {
  return (
    <section id="what-you-get" className="container py-24">
      <div className="flex flex-col gap-4 md:max-w-2xl">
        <span className="w-fit rounded-full border border-signal-500/40 bg-signal-900/40 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-signal-200">
          What you get
        </span>
        <h2 className="text-balance font-display text-3xl font-bold tracking-tight md:text-4xl">
          One line. Everything on it.
        </h2>
        <p className="text-pretty text-muted-foreground">
          No add-on packages, no sports tier, no separate charge on fight night.
          Every plan carries the full grid.
        </p>
      </div>

      <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {BENEFITS.map((item) => {
          const Icon = ICONS[item.icon] ?? Tv
          return (
            <article
              key={item.title}
              className="group flex flex-col gap-4 rounded-2xl border border-border bg-card p-7 transition-colors hover:border-signal-500/50"
            >
              <span className="grid size-11 place-items-center rounded-xl border border-signal-500/30 bg-signal-900/50 text-signal-200 transition-colors group-hover:text-signal-100">
                <Icon className="size-5" strokeWidth={1.75} />
              </span>
              <h3 className="font-display text-lg font-semibold tracking-tight">
                {item.title}
              </h3>
              <p className="text-pretty text-sm leading-relaxed text-muted-foreground">
                {item.body}
              </p>
            </article>
          )
        })}
      </div>
    </section>
  )
}
