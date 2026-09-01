import { STEPS } from "@/lib/offer"

export function HowItWorks() {
  return (
    <section id="how-it-works" className="relative overflow-hidden py-24">
      <div className="aura pointer-events-none absolute inset-x-0 top-0 h-96 opacity-60" />
      <div className="container relative">
        <div className="flex flex-col items-center gap-4 text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            On your TV in four steps
          </h2>
          <p className="max-w-xl text-pretty text-muted-foreground">
            Most customers are watching within minutes of paying. All you need
            is the MAC address printed on the back of the box.
          </p>
        </div>

        <div className="relative mt-14">
          <div className="hairline absolute inset-x-8 top-6 hidden h-px lg:block" />
          <ol className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {STEPS.map((item, i) => (
              <li
                key={item.step}
                className="relative flex flex-col gap-3 rounded-2xl border border-border bg-card p-6"
              >
                <span className="absolute -top-3 left-6 grid size-6 place-items-center rounded-full bg-signal-500 font-display text-xs font-bold text-white">
                  {i + 1}
                </span>
                <span className="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-signal-300">
                  {item.step}
                </span>
                <h3 className="font-display text-base font-semibold tracking-tight">
                  {item.title}
                </h3>
                <p className="text-pretty text-sm leading-relaxed text-muted-foreground">
                  {item.body}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  )
}
