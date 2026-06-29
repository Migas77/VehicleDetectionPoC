import { cn } from '@/lib/utils';

const NAV_ITEMS = [
    { key: 'overview', label: 'Overview', active: true },
    { key: 'dashboard', label: 'Dashboard', active: false },
    { key: 'map', label: 'Map', active: false },
    { key: 'camera', label: 'Camera', active: false },
    { key: 'notifications', label: 'Notifications', active: false },
] as const;

export function LandingNav() {
    return (
        <header
            className="sticky top-0 z-50 border-b border-[#E6E4DC]"
            style={{ background: 'rgba(244,243,238,0.86)', backdropFilter: 'blur(12px)' }}
        >
            <div className="max-w-[1320px] mx-auto px-4 sm:px-7 py-3.5 flex items-center gap-4 sm:gap-7">
                <div className="flex items-center gap-2.5 cursor-pointer shrink-0">
                    <div className="w-[34px] h-[34px] rounded-[9px] bg-[#16181B] flex items-center justify-content relative">
                        <div className="w-full h-full flex items-center justify-center relative">
                            <div className="w-[13px] h-[13px] rounded-full border-[2.5px] border-[#E4FB52]" />
                            <div className="absolute w-1 h-1 rounded-full bg-[#E4FB52]" />
                        </div>
                    </div>
                    <div className="flex flex-col leading-none">
                        <span className="font-grotesk font-bold text-[18px] tracking-[-0.02em] text-[#16181B]">
                            VIGIA
                        </span>
                        <span className="font-jetbrains text-[8.5px] tracking-[0.18em] text-[#8A8C86] mt-[3px]">
                            CRASH RESPONSE
                        </span>
                    </div>
                </div>

                <nav className="hidden md:flex items-center gap-1 ml-3">
                    {NAV_ITEMS.map((item) => (
                        <div
                            key={item.key}
                            className={cn(
                                'px-3.5 py-2 rounded-[9px] cursor-pointer text-[14.5px] font-medium transition-colors',
                                item.active
                                    ? 'bg-white text-[#16181B]'
                                    : 'text-[#5C5E57] hover:bg-white/60',
                            )}
                        >
                            {item.label}
                        </div>
                    ))}
                </nav>

                <div className="ml-auto flex items-center gap-3.5">
                    <div className="hidden sm:flex items-center gap-2 px-3 py-[7px] rounded-[20px] bg-white border border-[#E6E4DC]">
                        <span
                            className="w-2 h-2 rounded-full bg-[#2F9E63]"
                            style={{ animation: 'vg-blink 1.6s ease-in-out infinite' }}
                        />
                        <span className="font-jetbrains text-[11.5px] text-[#45473F]">
                            SYSTEM ONLINE
                        </span>
                    </div>
                    <button
                        type="button"
                        className="px-[18px] py-[10px] rounded-[10px] bg-[#16181B] text-[#F4F3EE] font-semibold text-[14px] flex items-center gap-2 cursor-pointer whitespace-nowrap"
                    >
                        Live dashboard
                        <span className="w-1.5 h-1.5 rounded-full bg-[#E4FB52]" />
                    </button>
                </div>
            </div>
        </header>
    );
}
