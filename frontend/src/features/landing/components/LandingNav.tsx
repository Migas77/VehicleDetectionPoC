import { useRef } from 'react';

import { cn } from '@/lib/utils';

const NAV_ITEMS = [
    { key: 'overview', label: 'Overview', active: true },
    { key: 'dashboard', label: 'Dashboard', active: false },
    { key: 'map', label: 'Map', active: false },
    { key: 'camera', label: 'Camera', active: false },
    { key: 'notifications', label: 'Notifications', active: false },
] as const;

export function LandingNav() {
    const btnSheenRef = useRef<HTMLSpanElement>(null);

    const handleBtnMouseEnter = () => {
        const el = btnSheenRef.current;
        if (!el) return;
        el.getAnimations().forEach((a) => a.cancel());
        el.animate([{ transform: 'translate(-125%)' }, { transform: 'translate(125%)' }], {
            duration: 550,
            easing: 'cubic-bezier(0.33,1,0.68,1)',
            fill: 'none',
        });
    };

    return (
        <header className="fixed top-0 left-0 right-0 z-50 pointer-events-none px-4 sm:px-7 pt-4">
            <nav className="relative mx-auto flex max-w-[1320px] items-center justify-between gap-3">
                {/* Logo pill */}
                <div
                    className={cn(
                        'group/logo pointer-events-auto relative inline-flex shrink-0 items-center gap-2.5 overflow-hidden',
                        'rounded-2xl border border-neutral-200/80 bg-white/80 px-2 py-1.5 pr-3.5',
                        'shadow-[0_6px_18px_-6px_rgba(15,15,15,0.18),0_1px_2px_rgba(0,0,0,0.04)]',
                        'backdrop-blur-md',
                        'transition-[background-color,border-color,box-shadow,transform] duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]',
                        'hover:border-neutral-300 hover:bg-white hover:shadow-[0_14px_30px_-8px_rgba(15,15,15,0.28),0_1px_2px_rgba(0,0,0,0.04)]',
                        'active:scale-[0.98] cursor-pointer',
                    )}
                >
                    <span className="vg-sheen-overlay" aria-hidden="true" />

                    <div className="relative flex w-[34px] h-[34px] items-center justify-center rounded-[9px] bg-[#16181B] ring-1 ring-black/10 transition-transform duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] group-hover/logo:scale-[1.06] group-hover/logo:-rotate-[7deg]">
                        <div className="w-[13px] h-[13px] rounded-full border-[2.5px] border-[#E4FB52]" />
                        <div className="absolute w-1 h-1 rounded-full bg-[#E4FB52]" />
                    </div>

                    <div className="flex flex-col leading-none">
                        <span className="font-grotesk font-bold text-[17px] tracking-[-0.02em] text-[#16181B] transition-colors duration-300 group-hover/logo:text-black">
                            VIGIA
                        </span>
                        <span className="font-jetbrains text-[8px] tracking-[0.18em] text-[#8A8C86] mt-[3px]">
                            CRASH RESPONSE
                        </span>
                    </div>
                </div>

                {/* Right pill: nav links + status + CTA */}
                <div
                    className={cn(
                        'pointer-events-auto inline-flex shrink-0 flex-wrap items-center justify-end gap-1',
                        'rounded-full border border-neutral-200/80 bg-white/80 px-1.5 py-1.5',
                        'shadow-[0_6px_18px_-6px_rgba(15,15,15,0.18),0_1px_2px_rgba(0,0,0,0.04)]',
                        'backdrop-blur-md',
                        'transition-[box-shadow,border-color] duration-300 ease-out',
                        'hover:border-neutral-300/90 hover:shadow-[0_10px_26px_-10px_rgba(15,15,15,0.22),0_1px_2px_rgba(0,0,0,0.04)]',
                    )}
                >
                    <nav className="hidden md:flex items-center gap-0.5">
                        {NAV_ITEMS.map((item) => (
                            <div
                                key={item.key}
                                className={cn(
                                    'relative h-9 inline-flex items-center overflow-hidden rounded-full px-3.5 cursor-pointer',
                                    'text-sm font-medium antialiased',
                                    'transition-[color,transform,box-shadow] duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]',
                                    'hover:-translate-y-px hover:text-neutral-900 hover:shadow-[0_6px_16px_-8px_rgba(15,15,15,0.22)]',
                                    'active:translate-y-0 active:scale-[0.98]',
                                    item.active
                                        ? 'bg-black/5 text-neutral-900'
                                        : 'text-neutral-600',
                                )}
                            >
                                {item.label}
                            </div>
                        ))}
                    </nav>

                    <div className="hidden md:block w-px h-5 bg-neutral-200 mx-1" />

                    <div className="hidden sm:flex items-center gap-1.5 px-3 h-9 rounded-full">
                        <span
                            className="w-1.5 h-1.5 rounded-full bg-[#2F9E63] shrink-0"
                            style={{ animation: 'vg-blink 1.6s ease-in-out infinite' }}
                        />
                        <span className="font-jetbrains text-[10.5px] text-[#45473F] tracking-wide whitespace-nowrap">
                            SYSTEM ONLINE
                        </span>
                    </div>

                    <button
                        type="button"
                        onMouseEnter={handleBtnMouseEnter}
                        className={cn(
                            'relative inline-flex h-9 items-center gap-1.5 overflow-hidden rounded-full',
                            'bg-[#16181B] px-4 text-[13px] font-semibold text-[#F4F3EE]',
                            'shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] ring-1 ring-black/20',
                            'transition-[transform,box-shadow] duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]',
                            'hover:-translate-y-px hover:shadow-[0_6px_16px_-8px_rgba(15,15,15,0.4)]',
                            'active:translate-y-0 active:scale-[0.98] cursor-pointer whitespace-nowrap',
                        )}
                    >
                        <span
                            ref={btnSheenRef}
                            aria-hidden="true"
                            className="pointer-events-none absolute inset-0 bg-gradient-to-r from-transparent via-white/22 to-transparent"
                            style={{ transform: 'translate(-125%)' }}
                        />
                        Live dashboard
                        <span className="w-1.5 h-1.5 rounded-full bg-[#E4FB52] shrink-0" />
                    </button>
                </div>
            </nav>
        </header>
    );
}
