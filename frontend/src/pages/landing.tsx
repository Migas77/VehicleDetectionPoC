import {
    CtaSection,
    FeaturesSection,
    LandingFooter,
    LandingHero,
    LandingNav,
    PipelineSection,
    PpdrSection,
    TrustStrip,
} from '@/features/landing';

export function LandingPage() {
    return (
        <div className="min-h-screen font-dm" style={{ background: '#F4F3EE', color: '#16181B' }}>
            <LandingNav />
            <main className="pt-20">
                <LandingHero />
                <TrustStrip />
                <FeaturesSection />
                <PipelineSection />
                <PpdrSection />
                <CtaSection />
            </main>
            <LandingFooter />
        </div>
    );
}
