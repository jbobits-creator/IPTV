/**
 * Single source of truth for the offer page copy.
 * Anything wrapped in [SQUARE BRACKETS] is a placeholder: swap it for your
 * real value before the page goes live.
 */

export const BRAND = "[YOUR BRAND]"

export const CONTACT = {
  email: "[YOUR EMAIL]",
  whatsapp: "[YOUR WHATSAPP NUMBER]",
  telegram: "[YOUR TELEGRAM]",
}

export const OFFER_LINE =
  "We supply IPTV to MAG boxes anywhere on the globe that has internet."

export const HEADLINE_NUMBERS = [
  { value: "20,000", label: "Live TV channels", note: "Worldwide line-up" },
  { value: "30,000+", label: "VOD & TV series", note: "Films and box sets" },
  { value: "All sports", label: "Incl. 3pm kickoffs", note: "Plus PPV events" },
  { value: "2 weeks", label: "Catch-up", note: "Rewind any channel" },
]

export const BENEFITS = [
  {
    icon: "tv",
    title: "20,000 live channels",
    body: "Entertainment, news, kids, documentaries and sport from every region — one line, one portal, the full grid.",
  },
  {
    icon: "film",
    title: "Over 30,000 VOD & series",
    body: "Films and complete TV series on demand, added to continuously, browsable straight from the MAG portal.",
  },
  {
    icon: "trophy",
    title: "All sport, including 3pm kickoffs",
    body: "Full sports coverage across the leagues, with the 3pm Saturday kickoffs that domestic broadcasters do not carry.",
  },
  {
    icon: "ticket",
    title: "PPV events included",
    body: "Boxing, MMA and the big one-off pay-per-view cards are part of the line — no extra charge on the night.",
  },
  {
    icon: "rewind",
    title: "2 week catch-up",
    body: "Missed it? Scroll back up to fourteen days on catch-up enabled channels and watch it whenever you like.",
  },
  {
    icon: "globe",
    title: "Anywhere with internet",
    body: "Your MAG box works wherever it is plugged in — at home, abroad or in a second property. If it reaches the internet, it reaches us.",
  },
]

export const STEPS = [
  {
    step: "Step 1",
    title: "Choose your package",
    body: "Pick 1, 3, 6 or 12 months and how many connections you need for the household.",
  },
  {
    step: "Step 2",
    title: "Send us your MAC",
    body: "Give us the MAC address from your MAG box — Settings, then System Settings, then About.",
  },
  {
    step: "Step 3",
    title: "We load your portal",
    body: "Your line is registered against that MAC and the portal URL is emailed to you, usually within minutes.",
  },
  {
    step: "Step 4",
    title: "Enter it and watch",
    body: "Settings, Servers, Portals — paste the URL, reboot the box, and the full grid loads on your TV.",
  },
]

export const DEVICES = [
  "MAG 250",
  "MAG 254",
  "MAG 256",
  "MAG 322",
  "MAG 324",
  "MAG 349",
  "MAG 420 4K",
  "MAG 524 4K",
  "Formuler Z",
  "Android TV",
  "Amazon Firestick",
  "Smart TV apps",
  "Enigma2",
  "iOS & Android",
  "VLC / Kodi",
]

export const PLANS = [
  {
    name: "1 Month",
    period: "per month",
    price: "[YOUR PRICE]",
    blurb: "Try the full line with nothing locked in.",
    featured: false,
  },
  {
    name: "3 Months",
    period: "per quarter",
    price: "[YOUR PRICE]",
    blurb: "A season of sport on one payment.",
    featured: false,
  },
  {
    name: "6 Months",
    period: "per half year",
    price: "[YOUR PRICE]",
    blurb: "Half a year, one setup, no renewals to remember.",
    featured: true,
  },
  {
    name: "12 Months",
    period: "per year",
    price: "[YOUR PRICE]",
    blurb: "Best value per month for a permanent setup.",
    featured: false,
  },
]

export const PLAN_FEATURES = [
  "20,000 live TV channels",
  "30,000+ VOD & TV series",
  "All sports, 3pm kickoffs & PPV",
  "2 week catch-up",
  "HD, FHD & 4K where broadcast",
  "MAG portal set up for you",
]

export const FAQS = [
  {
    q: "Which MAG boxes does this work on?",
    a: "Every current MAG portal box — 250, 254, 256, 322, 324, 349, 420 and 524 among them. We register your line against the box's MAC address and send a portal URL you paste into Settings, Servers, Portals.",
  },
  {
    q: "Will it work in my country?",
    a: "Yes. The line is delivered over the open internet, so the box works anywhere it can get online. A stable connection of around 15 Mbps is comfortable for HD and 25 Mbps for 4K.",
  },
  {
    q: "What exactly does 2 week catch-up cover?",
    a: "On catch-up enabled channels you can scroll back through the last fourteen days of programming from the EPG and start anything from the beginning.",
  },
  {
    q: "Are the 3pm kickoffs and PPV cards really included?",
    a: "Yes — full sports coverage is part of the standard line, including the Saturday 3pm kickoffs and pay-per-view events. There is no separate charge on fight night.",
  },
  {
    q: "Can I watch on more than one device at a time?",
    a: "Each connection streams one device at a time. Add extra connections for other rooms or family members — tell us how many you need and we will price it.",
  },
  {
    q: "Do you offer a trial?",
    a: "We do. Ask for a trial line, give us the MAC address of your MAG box, and see the grid on your own TV before you pay for anything.",
  },
]
