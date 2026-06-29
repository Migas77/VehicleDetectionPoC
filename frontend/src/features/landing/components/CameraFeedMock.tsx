export function CameraFeedMock() {
    return (
        <div
            className="relative bg-[#16181B] rounded-[22px] p-[18px]"
            style={{ boxShadow: '0 30px 70px -30px rgba(22,24,27,0.5)' }}
        >
            <div className="flex items-center justify-between px-1.5 pb-3.5">
                <div className="flex items-center gap-2">
                    <span
                        className="w-[9px] h-[9px] rounded-full bg-[#E5484D]"
                        style={{ animation: 'vg-blink 1.4s ease-in-out infinite' }}
                    />
                    <span className="font-jetbrains text-[11px] text-[#E4FB52] tracking-[0.08em]">
                        LIVE · AVEIRO
                    </span>
                </div>
                <span className="font-jetbrains text-[11px] text-[#6F726B]">CAM-02</span>
            </div>

            {/* Road scene */}
            <div
                className="relative h-[188px] rounded-[13px] overflow-hidden"
                style={{
                    background: 'linear-gradient(180deg, #20242A 0%, #14161A 55%, #0F1013 100%)',
                }}
            >
                {/* Road surface */}
                <div
                    className="absolute bottom-0 left-0 right-0 h-[64%]"
                    style={{
                        background: 'linear-gradient(180deg, #2a2d33, #1b1d22)',
                        clipPath: 'polygon(38% 0, 62% 0, 100% 100%, 0 100%)',
                    }}
                />
                {/* Dashed center line */}
                <div
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-[64%] opacity-50"
                    style={{
                        background:
                            'repeating-linear-gradient(#E4FB52 0 10px, transparent 10px 26px)',
                        clipPath: 'polygon(40% 0, 60% 0, 100% 100%, 0 100%)',
                    }}
                />
                {/* Crash bounding box */}
                <div
                    className="absolute border-2 border-[#E5484D] rounded-[4px]"
                    style={{
                        left: '38%',
                        top: '52%',
                        width: '96px',
                        height: '70px',
                        animation: 'vg-flash 1.1s ease-in-out infinite',
                    }}
                >
                    <span
                        className="absolute -top-5 -left-0.5 font-jetbrains text-[10px] text-white px-1.5 py-px rounded-[3px]"
                        style={{ background: '#E5484D' }}
                    >
                        CRASH 0.94
                    </span>
                </div>
                {/* Car bounding box */}
                <div
                    className="absolute border-[1.5px] border-[rgba(228,251,82,0.7)] rounded-[4px]"
                    style={{ left: '14%', top: '60%', width: '52px', height: '38px' }}
                >
                    <span
                        className="absolute -top-[17px] left-0 font-jetbrains text-[9px] text-[#16181B] px-[5px] py-px rounded-[3px]"
                        style={{ background: 'rgba(228,251,82,0.9)' }}
                    >
                        CAR
                    </span>
                </div>
                {/* Scan line */}
                <div
                    className="absolute left-0 right-0 h-0.5"
                    style={{
                        background:
                            'linear-gradient(90deg, transparent, rgba(228,251,82,0.5), transparent)',
                        animation: 'vg-scan 3.5s linear infinite',
                    }}
                />
            </div>

            {/* Alert toast */}
            <div className="mt-3.5 bg-[#1E2025] border border-[#2C2F35] rounded-[13px] p-[13px] flex gap-3 items-start">
                <div className="w-9 h-9 rounded-[9px] bg-[rgba(229,72,77,0.16)] flex items-center justify-center shrink-0">
                    <div className="relative w-4 h-4">
                        <div className="w-4 h-4 rounded-full border-2 border-[#E5484D]" />
                        <div
                            className="absolute inset-[-2px] rounded-full border-2 border-[#E5484D]"
                            style={{ animation: 'vg-pulse 1.8s ease-out infinite' }}
                        />
                    </div>
                </div>
                <div className="flex-1 min-w-0">
                    <div className="text-[#F4F3EE] font-semibold text-[14px]">
                        Collision detected — Av. Dr. Lourenço Peixinho
                    </div>
                    <div className="text-[#9A9C95] text-[12.5px] mt-0.5">
                        Broadcast to 7 pedestrians · 4 vehicles within 250 m
                    </div>
                </div>
                <span className="font-jetbrains text-[10px] text-[#6F726B] shrink-0">now</span>
            </div>
        </div>
    );
}
