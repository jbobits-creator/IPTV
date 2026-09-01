import Link from "next/link"

import { BRAND, CONTACT } from "@/lib/offer"

const COLUMNS = [
  {
    title: "Service",
    links: ["What you get", "How it works", "Devices", "Plans"],
  },
  {
    title: "Support",
    links: ["Setup guide", "FAQ", "Contact us", "Reseller programme"],
  },
  {
    title: "Legal",
    links: ["Terms of service", "Refund policy", "Privacy policy"],
  },
]

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-card/40">
      <div className="container grid gap-12 py-16 md:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div className="flex flex-col gap-4">
          <span className="font-display text-lg font-bold tracking-tight">
            {BRAND}
          </span>
          <p className="max-w-xs text-pretty text-sm leading-relaxed text-muted-foreground">
            IPTV supplied to MAG boxes anywhere on the globe that has internet.
          </p>
          <dl className="flex flex-col gap-1.5 text-sm">
            <div className="flex gap-2">
              <dt className="text-muted-foreground">Email</dt>
              <dd className="text-signal-200">{CONTACT.email}</dd>
            </div>
            <div className="flex gap-2">
              <dt className="text-muted-foreground">WhatsApp</dt>
              <dd className="text-signal-200">{CONTACT.whatsapp}</dd>
            </div>
            <div className="flex gap-2">
              <dt className="text-muted-foreground">Telegram</dt>
              <dd className="text-signal-200">{CONTACT.telegram}</dd>
            </div>
          </dl>
        </div>

        {COLUMNS.map((column) => (
          <div key={column.title} className="flex flex-col gap-4">
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-signal-200">
              {column.title}
            </h3>
            <ul className="flex flex-col gap-2.5">
              {column.links.map((link) => (
                <li key={link}>
                  <Link
                    href="#"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="border-t border-border">
        <div className="container flex flex-col gap-2 py-6 text-xs text-muted-foreground md:flex-row md:items-center md:justify-between">
          <p>
            © {new Date().getFullYear()} {BRAND}. All rights reserved.
          </p>
          <p>Subscriptions cover the service only. No hardware included.</p>
        </div>
      </div>
    </footer>
  )
}
