const STEPS = [
    {
        step: '01',
        glyph: '◉',
        iconBg: '#16181B',
        iconColor: '#E4FB52',
        title: 'Capture',
        body: 'Roadside cameras stream the scene to an edge node inside the 5G slice.',
    },
    {
        step: '02',
        glyph: '⚡',
        iconBg: '#E4FB52',
        iconColor: '#16181B',
        title: 'Detect',
        body: 'On-device CV model classifies the collision and scores confidence in <60 ms.',
    },
    {
        step: '03',
        glyph: '↗',
        iconBg: '#16181B',
        iconColor: '#E4FB52',
        title: 'Expose',
        body: 'NEF + CAMARA resolve who is nearby and open a priority channel via CAPIF.',
    },
    {
        step: '04',
        glyph: '◈',
        iconBg: '#E4FB52',
        iconColor: '#16181B',
        title: 'Warn',
        body: 'Pedestrians, vehicles and responders are alerted within the 250 m impact radius.',
    },
] as const;

export function PipelineSection() {
    return (
        <section className="max-w-[1320px] mx-auto px-4 sm:px-7 pt-[70px] pb-5">
            <div className="font-jetbrains text-[12px] tracking-[0.12em] text-[#8A8C86]">
                [ 02 ] HOW IT WORKS
            </div>
            <h2 className="font-grotesk font-bold text-[32px] sm:text-[40px] tracking-[-0.025em] mt-3 mb-9 leading-[1.08] text-[#16181B]">
                From impact to alert in four hops
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
                {STEPS.map((s) => (
                    <div
                        key={s.step}
                        className="bg-white border border-[#EAE8E0] rounded-[18px] p-6 relative"
                    >
                        <div className="font-jetbrains text-[12px] text-[#B6B4AA]">{s.step}</div>
                        <div
                            className="w-10 h-10 rounded-[11px] mt-3.5 mb-4 flex items-center justify-center font-grotesk font-bold text-[18px]"
                            style={{ background: s.iconBg, color: s.iconColor }}
                        >
                            {s.glyph}
                        </div>
                        <h3 className="font-grotesk font-semibold text-[18px] m-0 tracking-[-0.01em] text-[#16181B]">
                            {s.title}
                        </h3>
                        <p className="text-[#54564F] text-[13.5px] leading-[1.55] mt-2 mb-0">
                            {s.body}
                        </p>
                    </div>
                ))}
            </div>
        </section>
    );
}
