const FEATURE_CARDS = [
    {
        tag: '5G',
        title: '5G Core via NEF',
        body: 'Network Exposure Function gives VIGIA secure, policy-controlled access to device location and QoS — alerts ride the operator network, not the public internet.',
    },
    {
        tag: 'API',
        title: 'CAMARA APIs',
        body: 'Standardised CAMARA endpoints (Device Location, Device Status, Quality-on-Demand) let any operator integrate the same way, anywhere.',
    },
    {
        tag: 'CAP',
        title: 'Secured by CAPIF',
        body: 'The Common API Framework authenticates and authorises every service call between VIGIA, the cameras and the 5G core — zero implicit trust.',
    },
    {
        tag: 'MSG',
        title: 'Notifications',
        body: 'SMS alerts reach nearby pedestrians. CCAM DENM messages are multicasted directly to connected vehicles using a geospatial quadtree tiling scheme.',
    },
] as const;

export function FeaturesSection() {
    return (
        <section className="max-w-[1320px] mx-auto px-4 sm:px-7 pt-[78px] pb-5">
            <div>
                <div className="font-jetbrains text-[12px] tracking-[0.12em] text-[#8A8C86]">
                    [ 01 ] CAPABILITIES
                </div>
                <h2 className="font-grotesk font-bold text-[32px] sm:text-[40px] tracking-[-0.025em] mt-3 mb-0 max-w-[620px] leading-[1.08] text-[#16181B]">
                    A complete response loop,
                    <br />
                    from lens to alert
                </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-[18px] mt-10">
                {/* Big dark card */}
                <div className="sm:row-span-2 bg-[#16181B] rounded-[20px] p-8 text-[#F4F3EE] flex flex-col min-h-[320px] sm:min-h-[360px]">
                    <div className="inline-flex w-[46px] h-[46px] rounded-[12px] bg-[#E4FB52] items-center justify-center shrink-0">
                        <div className="relative w-[18px] h-[18px] border-[2.5px] border-[#16181B] rounded-[5px]">
                            <div className="absolute inset-[3px] rounded-sm bg-[#16181B]" />
                        </div>
                    </div>
                    <h3 className="font-grotesk font-semibold text-[26px] mt-6 mb-0 tracking-[-0.02em]">
                        AI crash detection
                    </h3>
                    <p className="text-[#A6A8A1] text-[15px] leading-[1.6] mt-3 mb-0">
                        A computer‑vision model, running at the edge, observes each roadside camera
                        video stream, classifying vehicle collisions frame‑by‑frame, with a
                        confidence scoring.
                    </p>
                    <div className="mt-auto pt-6 flex gap-6">
                        <div>
                            <div className="font-grotesk font-bold text-[24px] text-[#E4FB52]">
                                30fps
                            </div>
                            <div className="text-[12.5px] text-[#84867F] mt-0.5">
                                edge inference
                            </div>
                        </div>
                        <div>
                            <div className="font-grotesk font-bold text-[24px] text-[#E4FB52]">
                                100%
                            </div>
                            <div className="text-[12.5px] text-[#84867F] mt-0.5">automation</div>
                        </div>
                    </div>
                </div>

                {/* Three white cards */}
                {FEATURE_CARDS.map((card) => (
                    <div
                        key={card.title}
                        className="bg-white border border-[#EAE8E0] rounded-[20px] p-7"
                    >
                        <div className="flex items-center gap-3.5">
                            <div className="w-[42px] h-[42px] rounded-[11px] bg-[#F1F0EA] border border-[#E6E4DC] flex items-center justify-center font-jetbrains font-semibold text-[#16181B] text-[13px] shrink-0">
                                {card.tag}
                            </div>
                            <h3 className="font-grotesk font-semibold text-[19px] m-0 tracking-[-0.01em] text-[#16181B]">
                                {card.title}
                            </h3>
                        </div>
                        <p className="text-[#54564F] text-[14.5px] leading-[1.6] mt-3.5 mb-0">
                            {card.body}
                        </p>
                    </div>
                ))}
            </div>
        </section>
    );
}
