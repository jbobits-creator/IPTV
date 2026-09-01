import { Check } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { PLANS, PLAN_FEATURES } from "@/lib/offer"

export function Plans() {
  return (
    <section id="plans" className="relative overflow-hidden py-24">
      <div className="aura pointer-events-none absolute inset-x-0 bottom-0 h-[520px] rotate-180 opacity-70" />
      <div className="container relative">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="rounded-full border border-signal-500/40 bg-signal-900/40 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-signal-200">
            Plans
          </span>
          <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            Pick a length. The line never changes.
          </h2>
          <p className="max-w-xl text-pretty text-muted-foreground">
            Every plan carries all 20,000 channels, the full VOD library, the
            sport and the catch-up. Longer plans simply cost less per month.
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {PLANS.map((plan) => (
            <article
              key={plan.name}
              className={cn(
                "relative flex flex-col gap-6 rounded-2xl border border-border bg-card p-7",
                plan.featured &&
                  "border-signal-500/60 bg-gradient-to-b from-signal-900/60 to-card shadow-[0_30px_80px_-40px_rgba(139,47,232,0.9)]",
              )}
            >
              {plan.featured && (
                <span className="absolute -top-3 right-6 rounded-full bg-kick px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-white">
                  Most popular
                </span>
              )}

              <div className="flex flex-col gap-2">
                <h3 className="font-display text-lg font-semibold tracking-tight">
                  {plan.name}
                </h3>
                <p className="text-sm text-muted-foreground">{plan.blurb}</p>
              </div>

              <div className="flex flex-col gap-1">
                <span className="font-display text-3xl font-bold tracking-tight text-white">
                  {plan.price}
                </span>
                <span className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                  {plan.period} · 1 connection
                </span>
              </div>

              <ul className="flex flex-col gap-2.5">
                {PLAN_FEATURES.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5 text-sm">
                    <Check
                      className="mt-0.5 size-4 shrink-0 text-signal-300"
                      strokeWidth={2.5}
                    />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant={plan.featured ? "default" : "outline"}
                className="mt-auto w-full"
              >
                Start now
              </Button>
            </article>
          ))}
        </div>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Need two, three or four connections for the household? Ask us and we
          will price it for you.
        </p>
      </div>
    </section>
  )
}
