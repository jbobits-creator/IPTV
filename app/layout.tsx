import type { Metadata } from "next"
import { Archivo, Manrope } from "next/font/google"

import "./globals.css"

const display = Archivo({
  subsets: ["latin"],
  style: ["normal", "italic"],
  weight: ["500", "600", "700", "800"],
  variable: "--font-display",
})

const body = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body",
})

export const metadata: Metadata = {
  title: "IPTV for MAG boxes, anywhere with internet",
  description:
    "20,000 live TV channels, over 30,000 VOD and TV series, all sports including 3pm kickoffs and PPV, plus 2 week catch-up — delivered to your MAG box anywhere on the globe.",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className={`${display.variable} ${body.variable} font-sans`}>
        {children}
      </body>
    </html>
  )
}
