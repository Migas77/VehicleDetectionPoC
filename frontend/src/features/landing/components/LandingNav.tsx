import { useState, useRef } from 'react';

import { Link, useRouterState } from '@tanstack/react-router';
import { Menu, X } from 'lucide-react';

import { cn } from '@/lib/utils';

type NavKey = 'overview' | 'dashboard' | 'map' | 'cameras' | 'notifications';

const NAV_ITEMS: { key: NavKey; label: string; badge?: number }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'map', label: 'Map' },
    { key: 'cameras', label: 'Cameras' },
    { key: 'notifications', label: 'Notifications', badge: 2 },
];

const ROUTES: Partial<Record<NavKey, '/' | '/notifications'>> = {
    overview: '/',
    notifications: '/notifications',
};

export function LandingNav() {
    const pathname = useRouterState({ select: (s) => s.location.pathname });
    const btnSheenRef = useRef<HTMLSpanElement>(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    function isActive(key: NavKey) {
        if (key === 'overview') return pathname === '/';
        const route = ROUTES[key];
        return route ? pathname === route : false;
    }

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

    const closeMenu = () => setIsMenuOpen(false);

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

                {/* Right section: pill + mobile dropdown */}
                <div className="pointer-events-auto relative">
                    {/* Right pill */}
                    <div
                        className={cn(
                            'inline-flex shrink-0 items-center gap-1',
                            'rounded-full border border-neutral-200/80 bg-white/80 px-1.5 py-1.5',
                            'shadow-[0_6px_18px_-6px_rgba(15,15,15,0.18),0_1px_2px_rgba(0,0,0,0.04)]',
                            'backdrop-blur-md',
                            'transition-[box-shadow,border-color] duration-300 ease-out',
                            'hover:border-neutral-300/90 hover:shadow-[0_10px_26px_-10px_rgba(15,15,15,0.22),0_1px_2px_rgba(0,0,0,0.04)]',
                        )}
                    >
                        {/* Desktop nav links */}
                        <nav className="hidden lg:flex items-center gap-0.5">
                            {NAV_ITEMS.map((item) => {
                                const active = isActive(item.key);
                                const cls = cn(
                                    'relative h-9 inline-flex items-center rounded-full px-3.5 cursor-pointer gap-1.5',
                                    'text-sm font-medium antialiased',
                                    'transition-[color,transform,box-shadow] duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]',
                                    'hover:-translate-y-px hover:text-neutral-900 hover:shadow-[0_6px_16px_-8px_rgba(15,15,15,0.22)]',
                                    'active:translate-y-0 active:scale-[0.98]',
                                    active ? 'bg-black/5 text-neutral-900' : 'text-neutral-600',
                                );
                                const badge =
                                    item.badge != null && item.badge > 0 ? (
                                        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-[5px] rounded-full bg-[#E5484D] font-jetbrains text-[11px] font-bold text-white flex-none tabular-nums">
                                            {item.badge}
                                        </span>
                                    ) : null;
                                const route = ROUTES[item.key];
                                return route ? (
                                    <Link key={item.key} to={route} className={cls}>
                                        {item.label}
                                        {badge}
                                    </Link>
                                ) : (
                                    <div key={item.key} className={cls}>
                                        {item.label}
                                        {badge}
                                    </div>
                                );
                            })}
                        </nav>

                        <div className="hidden lg:block w-px h-5 bg-neutral-200 mx-1" />

                        {/* System online - desktop only */}
                        <div className="hidden lg:flex items-center gap-1.5 px-3 h-9 rounded-full">
                            <span
                                className="w-1.5 h-1.5 rounded-full bg-[#2F9E63] shrink-0"
                                style={{ animation: 'vg-blink 1.6s ease-in-out infinite' }}
                            />
                            <span className="font-jetbrains text-[10.5px] text-[#45473F] tracking-wide whitespace-nowrap">
                                SYSTEM ONLINE
                            </span>
                        </div>

                        {/* CTA button */}
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

                        {/* Mobile hamburger toggle */}
                        <button
                            type="button"
                            onClick={() => setIsMenuOpen((v) => !v)}
                            aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
                            className={cn(
                                'lg:hidden relative inline-flex h-9 w-9 items-center justify-center rounded-full',
                                'text-neutral-700 transition-[background-color,transform] duration-200',
                                'hover:bg-black/5 active:scale-[0.95] cursor-pointer',
                            )}
                        >
                            {isMenuOpen ? (
                                <X size={18} strokeWidth={2} />
                            ) : (
                                <Menu size={18} strokeWidth={2} />
                            )}
                        </button>
                    </div>

                    {/* Mobile dropdown */}
                    {isMenuOpen && (
                        <div
                            className={cn(
                                'lg:hidden absolute right-0 top-full mt-2 min-w-[180px]',
                                'rounded-2xl border border-neutral-200/80 bg-white/95 backdrop-blur-md',
                                'shadow-[0_14px_30px_-8px_rgba(15,15,15,0.18),0_1px_2px_rgba(0,0,0,0.04)]',
                                'py-2 overflow-hidden',
                            )}
                        >
                            {NAV_ITEMS.map((item) => {
                                const active = isActive(item.key);
                                const cls = cn(
                                    'flex items-center gap-2 w-full px-4 py-2.5',
                                    'text-sm font-medium transition-colors duration-150',
                                    active
                                        ? 'text-neutral-900 bg-black/5'
                                        : 'text-neutral-500 hover:text-neutral-900 hover:bg-black/[0.03]',
                                );
                                const badge =
                                    item.badge != null && item.badge > 0 ? (
                                        <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-[5px] rounded-full bg-[#E5484D] font-jetbrains text-[11px] font-bold text-white flex-none tabular-nums">
                                            {item.badge}
                                        </span>
                                    ) : null;
                                const route = ROUTES[item.key];
                                return route ? (
                                    <Link
                                        key={item.key}
                                        to={route}
                                        className={cls}
                                        onClick={closeMenu}
                                    >
                                        {item.label}
                                        {badge}
                                    </Link>
                                ) : (
                                    <div key={item.key} className={cls}>
                                        {item.label}
                                        {badge}
                                    </div>
                                );
                            })}

                            <div className="mx-4 my-1 border-t border-neutral-100" />

                            <div className="flex items-center gap-1.5 px-4 py-2.5">
                                <span
                                    className="w-1.5 h-1.5 rounded-full bg-[#2F9E63] shrink-0"
                                    style={{ animation: 'vg-blink 1.6s ease-in-out infinite' }}
                                />
                                <span className="font-jetbrains text-[10.5px] text-[#45473F] tracking-wide">
                                    SYSTEM ONLINE
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </nav>
        </header>
    );
}
