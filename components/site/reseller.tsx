import { ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"

export function Reseller() {
  return (
    <section className="relative overflow-hidden border-t border-border">
      <div className="aura pointer-events-none absolute inset-x-0 bottom-[-40%] h-[700px] rotate-180" />
      <div className="container relative flex flex-col items-center gap-7 py-24 text-center">
        <h2 className="text-balance font-display text-3xl font-extrabold italic tracking-tight md:text-5xl">
          Sell it on. Join the reseller programme.
        </h2>
        <p className="max-w-xl text-pretty text-muted-foreground">
          Credits at wholesale rates, your own panel to create and renew lines,
          and the same 24/7 support behind you. Tell us the volume you expect
          and we will set your rate.
        </p>
        <Button size="lg" className="group">
          Become a reseller
          <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
        </Button>
      </div>
    </section>
  )
}
