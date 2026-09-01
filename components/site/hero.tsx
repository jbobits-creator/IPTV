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
  theta: 0.28,
  dark: 1,
  diffuse: 1.2,
  mapSamples: 16000,
  mapBrightness: 5.4,
  baseColor: [0.42, 0.28, 0.63],
  markerColor: [251 / 255, 100 / 255, 21 / 255],
  glowColor: [0.4, 0.19, 0.72],
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
      <div className="aura pointer-events-none absolute inset-x-0 -top-40 h-[720px]" />
      <div className="container relative pb-24 pt-16 md:pt-24">
        <div className="relative mx-auto flex max-w-3xl flex-col items-center gap-7 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-signal-500/40 bg-signal-900/40 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-signal-200">
            <span className="size-1.5 rounded-full bg-kick" />
            MAG box ready · delivered worldwide
          </span>

          <h1 className="text-balance font-display text-4xl font-extrabold italic leading-[1.04] tracking-tight md:text-6xl">
            IPTV for your MAG box,{" "}
            <span className="bg-gradient-to-b from-white to-signal-300 bg-clip-text text-transparent">
              anywhere the internet reaches
            </span>
          </h1>

          <p className="text-pretty max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
            20,000 live TV channels. Over 30,000 films and TV series on demand.
            All the sport, including the 3pm kickoffs and PPV. And two full
            weeks of catch-up on every enabled channel.
          </p>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Button size="lg" className="group">
              Start your free trial
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Button>
            <Button size="lg" variant="outline">
              <Play className="size-4" />
              See the channel line-up
            </Button>
          </div>
        </div>

        <div className="relative mt-4 h-[380px] md:h-[460px]">
          <Globe className="top-0 max-w-[560px]" />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(7,5,12,0.9),transparent_60%)]" />
        </div>

        <dl className="relative -mt-10 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border bg-border md:grid-cols-4">
          {HEADLINE_NUMBERS.map((item) => (
            <div
              key={item.label}
              className="flex flex-col gap-1 bg-card/90 px-6 py-7 backdrop-blur"
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
