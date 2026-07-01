export function CameraFeedPanel() {
    return (
        <div className="relative bg-[#16181B] rounded-[18px] p-3.5 shrink-0">
            <div className="flex items-center justify-between px-1 pb-3">
                <div className="flex items-center gap-2">
                    <span
                        className="w-2 h-2 rounded-full bg-[#E5484D]"
                        style={{ animation: 'vg-blink 1.4s ease-in-out infinite' }}
                    />
                    <span className="font-jetbrains text-[11px] text-[#E4FB52] tracking-[0.06em]">
                        REC · CAM-02
                    </span>
                </div>
                <span className="font-jetbrains text-[11px] text-[#8A8C86]">expand</span>
            </div>

            <div
                className="relative h-[196px] rounded-xl overflow-hidden"
                style={{
                    background: 'linear-gradient(180deg, #20242A 0%, #14161A 55%, #0F1013 100%)',
                }}
            >
                <div
                    className="absolute bottom-0 left-0 right-0 h-[64%]"
                    style={{
                        background: 'linear-gradient(180deg, #2a2d33, #1b1d22)',
                        clipPath: 'polygon(38% 0, 62% 0, 100% 100%, 0 100%)',
                    }}
                />
                <div
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-[64%] opacity-60"
                    style={{
                        background:
                            'repeating-linear-gradient(#E4FB52 0 10px, transparent 10px 26px)',
                        clipPath: 'polygon(40% 0, 60% 0, 100% 100%, 0 100%)',
                    }}
                />
                <div
                    className="absolute border-2 border-[#E5484D] rounded"
                    style={{
                        left: '36%',
                        top: '48%',
                        width: '84px',
                        height: '62px',
                        animation: 'vg-flash 1.1s ease-in-out infinite',
                    }}
                >
                    <span
                        className="absolute -top-4 -left-0.5 font-jetbrains text-[9px] text-white px-1.5 py-px rounded-[3px]"
                        style={{ background: '#E5484D' }}
                    >
                        CRASH 0.94
                    </span>
                </div>
                <div
                    className="absolute border-[1.5px] border-[rgba(228,251,82,0.7)] rounded"
                    style={{ left: '12%', top: '58%', width: '44px', height: '32px' }}
                >
                    <span
                        className="absolute -top-4 left-0 font-jetbrains text-[9px] text-[#16181B] px-[5px] py-px rounded-[3px]"
                        style={{ background: 'rgba(228,251,82,0.9)' }}
                    >
                        CAR
                    </span>
                </div>
                <div
                    className="absolute left-0 right-0 h-0.5"
                    style={{
                        background:
                            'linear-gradient(90deg, transparent, rgba(228,251,82,0.5), transparent)',
                        animation: 'vg-scan 3.5s linear infinite',
                    }}
                />
                <span className="absolute bottom-2 right-2.5 font-jetbrains text-[10px] text-[#E4FB52]">
                    DETECTOR ●
                </span>
            </div>
        </div>
    );
}
