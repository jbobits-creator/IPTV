# IPTV offer page

Landing page for an IPTV service supplied to MAG boxes, built around the
`Globe` component (cobe).

> **Placeholders** — everything in `[SQUARE BRACKETS]` in `lib/offer.ts`
> (brand name, prices, email, WhatsApp, Telegram) is a stand-in. Replace those
> values before the page goes live; nothing else needs editing to launch.

## Running it

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build + type check
```

## Project setup (what was added and why)

The repository was empty, so the whole shadcn-compatible stack was set up from
scratch. If you ever start again from a bare folder, this is the equivalent:

```bash
# 1. Next.js with TypeScript + Tailwind
npx create-next-app@14 . --typescript --tailwind --eslint --app --no-src-dir \
  --import-alias "@/*"

# 2. shadcn/ui — writes components.json, lib/utils.ts and the CSS variables
npx shadcn@latest init

# 3. the dependency the Globe component needs
npm install cobe
```

`npx shadcn@latest init` asks for a components directory. Keep the default,
`@/components` with UI primitives in **`components/ui`** — the shadcn CLI writes
every `npx shadcn@latest add <component>` into that exact folder and the
generated imports are hard-coded to `@/components/ui/<name>`. Putting primitives
anywhere else means every added component has to be re-pathed by hand, and
`components.json` is what the CLI reads to resolve those aliases.

### Layout

```
app/
  layout.tsx        fonts (Archivo + Manrope) and metadata
  page.tsx          the offer page — sections in order
  globals.css       Tailwind layers + the dark violet token set
components/
  ui/               shadcn primitives
    globe.tsx       the cobe globe (unmodified)
    button.tsx
  site/             page sections
    hero.tsx        globe + headline offer
    benefits.tsx    what is on the line
    how-it-works.tsx  MAC address -> portal URL -> watching
    devices.tsx     MAG models and everything else
    plans.tsx       1 / 3 / 6 / 12 months
    faq.tsx
    reseller.tsx
    site-header.tsx
    site-footer.tsx
lib/
  offer.ts          all page copy in one place
  utils.ts          cn()
components.json     shadcn config (aliases, Tailwind paths)
```

## The Globe component

`components/ui/globe.tsx` is the component as supplied, unchanged. It ships its
own light-coloured `GLOBE_CONFIG` default; the hero passes a violet config
instead, with markers on the cities the service is delivered to:

```tsx
<Globe className="top-0 max-w-[560px]" config={GLOBE} />
```

Two things to know:

- The component is `"use client"`, and a `config` contains an `onRender`
  function, so any component passing `config` must be a client component too —
  functions cannot cross the server/client boundary. That is why
  `components/site/hero.tsx` is marked `"use client"`.
- The canvas is absolutely positioned (`absolute inset-0`), so its parent needs
  `position: relative` and an explicit height.

Adding more shadcn primitives works as normal:

```bash
npx shadcn@latest add card badge accordion
```
