import { DEVICES } from "@/lib/offer"

export function Devices() {
  return (
    <section id="devices" className="border-y border-border bg-card/40 py-16">
      <div className="container flex flex-col items-center gap-3 text-center">
        <h2 className="font-display text-2xl font-bold tracking-tight md:text-3xl">
          Built for MAG — works on the rest too
        </h2>
        <p className="max-w-xl text-pretty text-sm text-muted-foreground">
          Set up on your MAG box by us, and usable on everything else you
          already own with the same line.
        </p>
      </div>

      <div className="relative mt-10 flex overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_12%,#000_88%,transparent)]">
        <ul className="flex w-max shrink-0 animate-marquee items-center gap-3 pr-3">
          {[...DEVICES, ...DEVICES].map((device, i) => (
            <li
              key={`${device}-${i}`}
              className="whitespace-nowrap rounded-full border border-border bg-background px-5 py-2.5 text-sm font-medium text-muted-foreground"
            >
              {device}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
