const PPDR_TAGS = [
    'Guaranteed QoS for responders',
    'Automatic incident dossier',
    'Mass road‑user warning',
] as const;

const PPDR_FLOW = [
    {
        dot: '#E5484D',
        title: 'Collision confirmed',
        sub: 'AI classifies impact at CAM-03',
        t: 'T+0.0s',
    },
    {
        dot: '#F5A524',
        title: 'Road users warned',
        sub: '250 m mass notification sent',
        t: 'T+0.2s',
    },
    {
        dot: '#2F9E63',
        title: 'Responders prioritised',
        sub: 'QoS slice + live feed to control room',
        t: 'T+0.6s',
    },
] as const;

export function PpdrSection() {
    return (
        <section className="max-w-[1320px] mx-auto px-4 sm:px-7 py-[70px]">
            <div className="rounded-[26px] p-8 sm:p-[52px] grid grid-cols-1 lg:grid-cols-[1fr_0.9fr] gap-10 lg:gap-12 items-center relative overflow-hidden bg-[#16181B]">
                {/* Glow */}
                <div
                    className="absolute -top-[60px] -right-[60px] w-[320px] h-[320px] rounded-full pointer-events-none"
                    style={{
                        background:
                            'radial-gradient(circle, rgba(228,251,82,0.12), transparent 70%)',
                    }}
                />

                {/* Left content */}
                <div className="relative">
                    <div
                        className="inline-flex items-center gap-2 px-3.5 py-[7px] rounded-[20px] font-jetbrains text-[11.5px] text-[#E4FB52]"
                        style={{
                            background: 'rgba(228,251,82,0.12)',
                            border: '1px solid rgba(228,251,82,0.3)',
                        }}
                    >
                        PPDR USE CASE
                    </div>
                    <h2 className="font-grotesk font-bold text-[30px] sm:text-[38px] tracking-[-0.025em] text-[#F4F3EE] mt-5 mb-0 leading-[1.08]">
                        Public Protection &amp; Disaster Relief, automated at the edge
                    </h2>
                    <p className="text-[#A6A8A1] text-[15.5px] leading-[1.65] mt-[18px] mb-0">
                        When VIGIA confirms a collision, it doesn't just warn road users; it
                        requests prioritised connectivity for first responders, pushes the incident
                        location and a live camera link to the control room, and keeps the alert
                        channel open until the scene is cleared.
                    </p>
                    <div className="flex flex-wrap gap-3 mt-6">
                        {PPDR_TAGS.map((tag) => (
                            <span
                                key={tag}
                                className="px-3.5 py-[9px] rounded-[10px] text-[#D7D8D2] text-[13.5px]"
                                style={{
                                    background: '#1E2025',
                                    border: '1px solid #2C2F35',
                                }}
                            >
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Right flow */}
                <div className="flex flex-col gap-3 relative">
                    {PPDR_FLOW.map((s) => (
                        <div
                            key={s.title}
                            className="rounded-[14px] px-[18px] py-4 flex items-center gap-3.5"
                            style={{ background: '#1B1D22', border: '1px solid #2A2D33' }}
                        >
                            <div
                                className="w-[30px] h-[30px] rounded-[8px] shrink-0"
                                style={{ background: s.dot }}
                            />
                            <div className="flex-1 min-w-0">
                                <div className="text-[#F4F3EE] font-semibold text-[14.5px]">
                                    {s.title}
                                </div>
                                <div className="text-[#8A8C86] text-[12.5px] mt-0.5">{s.sub}</div>
                            </div>
                            <span className="font-jetbrains text-[11px] text-[#E4FB52] shrink-0">
                                {s.t}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
