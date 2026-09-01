import { Benefits } from "@/components/site/benefits"
import { Devices } from "@/components/site/devices"
import { Faq } from "@/components/site/faq"
import { Hero } from "@/components/site/hero"
import { HowItWorks } from "@/components/site/how-it-works"
import { Plans } from "@/components/site/plans"
import { Reseller } from "@/components/site/reseller"
import { SiteFooter } from "@/components/site/site-footer"
import { SiteHeader } from "@/components/site/site-header"

export default function Page() {
  return (
    <>
      <SiteHeader />
      <main>
        <Hero />
        <Benefits />
        <HowItWorks />
        <Devices />
        <Plans />
        <Faq />
        <Reseller />
      </main>
      <SiteFooter />
    </>
  )
}
