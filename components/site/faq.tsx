import { Plus } from "lucide-react"

import { FAQS } from "@/lib/offer"

export function Faq() {
  return (
    <section id="faq" className="container py-24">
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-4 text-center">
        <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
          Questions we get asked
        </h2>
        <p className="text-pretty text-muted-foreground">
          Anything else, message us — we answer before you have paid a penny.
        </p>
      </div>

      <div className="mx-auto mt-12 flex max-w-3xl flex-col gap-3">
        {FAQS.map((item) => (
          <details
            key={item.q}
            className="group rounded-2xl border border-border bg-card px-6 py-5 transition-colors open:border-signal-500/50"
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-6 font-display text-base font-semibold tracking-tight [&::-webkit-details-marker]:hidden">
              {item.q}
              <Plus className="size-4 shrink-0 text-signal-300 transition-transform group-open:rotate-45" />
            </summary>
            <p className="text-pretty mt-4 text-sm leading-relaxed text-muted-foreground">
              {item.a}
            </p>
          </details>
        ))}
      </div>
    </section>
  )
}
