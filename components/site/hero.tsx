"use client"

import { COBEOptions } from "cobe"
import { ArrowRight, Play } from "lucide-react"

import { Globe } from "@/components/ui/globe"
import { Button } from "@/components/ui/button"
import { HEADLINE_NUMBERS } from "@/lib/offer"

/** Same globe, tuned to the violet of the page and marked with our delivery cities. */
const GLOBE: COBEOptions = {
  width: 800,
  height: 800,
  onRender: () => {},
  devicePixelRatio: 2,
  phi: 0,
  theta: 0.24,
  dark: 1,
  diffuse: 1.2,
  mapSamples: 16000,
  // mapBrightness alone lights only the sun-facing side; mapBaseBrightness is
  // what makes the continents readable while the globe spins.
  mapBrightness: 9,
  mapBaseBrightness: 0.13,
  baseColor: [0.3, 0.2, 0.48],
  markerColor: [251 / 255, 100 / 255, 21 / 255],
  glowColor: [0.44, 0.21, 0.78],
  markers: [
    { location: [51.5074, -0.1278], size: 0.1 },
    { location: [53.3498, -6.2603], size: 0.06 },
    { location: [40.7128, -74.006], size: 0.09 },
    { location: [43.6532, -79.3832], size: 0.06 },
    { location: [25.2048, 55.2708], size: 0.07 },
    { location: [-33.8688, 151.2093], size: 0.07 },
    { location: [19.076, 72.8777], size: 0.08 },
    { location: [6.5244, 3.3792], size: 0.06 },
    { location: [40.4168, -3.7038], size: 0.06 },
    { location: [52.52, 13.405], size: 0.06 },
    { location: [-23.5505, -46.6333], size: 0.07 },
  ],
}

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="aura pointer-events-none absolute inset-x-0 -top-52 h-[900px]" />

      {/* the globe rises behind the call to action and is dragged to spin */}
      <div className="absolute left-1/2 top-[420px] size-[520px] -translate-x-1/2 [mask-image:linear-gradient(to_bottom,transparent,#000_22%)] md:top-[470px] md:size-[760px]">
        <Globe className="max-w-none" config={GLOBE} />
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_46%,transparent_54%,rgba(7,5,12,0.7)_76%,#07050c_94%)]" />
      </div>

      <div className="container relative pb-20 pt-20 md:pt-28">
        <div className="pointer-events-none mx-auto flex max-w-3xl flex-col items-center gap-7 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-signal-500/40 bg-signal-900/50 px-4 py-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-signal-200 backdrop-blur md:text-xs md:tracking-[0.18em]">
            <span className="size-1.5 rounded-full bg-kick" />
            MAG box ready · delivered worldwide
          </span>

          <h1 className="text-balance font-display text-4xl font-extrabold italic leading-[1.04] tracking-tight [text-shadow:0_2px_40px_rgba(7,5,12,0.85)] md:text-6xl">
            IPTV for your MAG box,{" "}
            <span className="bg-gradient-to-b from-white to-signal-300 bg-clip-text text-transparent">
              anywhere the internet reaches
            </span>
          </h1>

          <p className="text-pretty max-w-2xl text-base leading-relaxed text-muted-foreground [text-shadow:0_2px_24px_rgba(7,5,12,0.9)] md:text-lg">
            20,000 live TV channels. Over 30,000 films and TV series on demand.
            All the sport, including the 3pm kickoffs and PPV. And two full
            weeks of catch-up on every enabled channel.
          </p>

          <div className="pointer-events-auto flex flex-col gap-3 sm:flex-row">
            <Button size="lg" className="group">
              Start your free trial
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Button>
            <Button size="lg" variant="outline" className="backdrop-blur">
              <Play className="size-4" />
              See the channel line-up
            </Button>
          </div>
        </div>

        <dl className="relative mt-[400px] grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border bg-border md:mt-[450px] md:grid-cols-4">
          {HEADLINE_NUMBERS.map((item) => (
            <div
              key={item.label}
              className="flex flex-col gap-1 bg-card/80 px-6 py-7 backdrop-blur-md"
            >
              <dt className="font-display text-2xl font-bold tracking-tight text-white md:text-3xl">
                {item.value}
              </dt>
              <dd className="text-sm font-semibold text-signal-200">
                {item.label}
              </dd>
              <dd className="text-xs text-muted-foreground">{item.note}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
