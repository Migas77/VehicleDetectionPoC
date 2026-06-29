const TECH = ['5G Core', '3GPP NEF', 'CAMARA APIs', 'CAPIF', 'CCAM'] as const;

export function TrustStrip() {
    return (
        <section className="border-t border-b border-[#E6E4DC] bg-white overflow-hidden">
            <div className="max-w-[1320px] mx-auto px-4 sm:px-7 py-[18px] flex items-center gap-8 sm:gap-10 flex-wrap">
                <span className="font-jetbrains text-[11.5px] text-[#9A9C95] whitespace-nowrap">
                    INTEROPERABLE WITH
                </span>
                <div className="flex flex-wrap gap-x-8 gap-y-2 items-center font-grotesk font-semibold text-[16px] text-[#54564F]">
                    {TECH.map((name, i) => (
                        <span key={name} className="flex items-center gap-8">
                            {i > 0 && <span className="text-[#C9C7BD]">·</span>}
                            {name}
                        </span>
                    ))}
                </div>
            </div>
        </section>
    );
}
