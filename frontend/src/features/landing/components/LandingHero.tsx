import { Fragment } from 'react';

import { CameraFeedMock } from './CameraFeedMock';

const STATS = [
    { value: '<180', unit: 'ms', label: 'detect → alert latency' },
    { value: '250', unit: 'm', label: 'alert broadcast radius' },
    { value: '24/7', unit: '', label: 'autonomous monitoring' },
] as const;

export function LandingHero() {
    return (
        <section className="max-w-[1320px] mx-auto px-4 sm:px-7 pt-14 sm:pt-16 pb-10">
            <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-10 lg:gap-14 items-center">
                {/* Left column */}
                <div>
                    <div className="inline-flex items-center gap-2 px-3.5 py-[7px] rounded-[20px] bg-white border border-[#E6E4DC] font-jetbrains text-[11.5px] tracking-[0.06em] text-[#45473F]">
                        <span
                            className="w-[7px] h-[7px] rounded-full bg-[#E4FB52]"
                            style={{ boxShadow: '0 0 0 3px rgba(228,251,82,0.25)' }}
                        />
                        AI INCIDENT RESPONSE · 5G CORE
                    </div>

                    <h1 className="font-grotesk font-bold text-[42px] sm:text-[52px] lg:text-[62px] tracking-[-0.03em] mt-[22px] mb-0 leading-[1.02] text-[#16181B]">
                        Detect crashes.
                        <br />
                        Warn everyone{' '}
                        <span
                            className="relative whitespace-nowrap"
                            style={{ isolation: 'isolate' }}
                        >
                            nearby
                            <span
                                className="absolute left-0 right-0 bottom-[6px] h-[14px] -z-10 rounded-[3px]"
                                style={{ background: '#E4FB52' }}
                            />
                        </span>
                        <br />
                        in milliseconds.
                    </h1>

                    <p className="text-[18px] leading-[1.6] text-[#54564F] max-w-[480px] mt-6 mb-0">
                        VIGIA watches the road through roadside cameras, detects collisions with
                        on‑device AI, and instantly alerts the pedestrians and vehicles around the
                        impact — over the 5G core, before help is even called.
                    </p>

                    <div className="flex flex-wrap gap-3 mt-8">
                        <button
                            type="button"
                            className="px-6 py-3.5 rounded-[11px] bg-[#16181B] text-[#F4F3EE] font-semibold text-[15.5px] cursor-pointer"
                        >
                            Open live dashboard →
                        </button>
                        <button
                            type="button"
                            className="px-6 py-3.5 rounded-[11px] bg-white border border-[#DEDCD3] text-[#16181B] font-semibold text-[15.5px] cursor-pointer"
                        >
                            Watch detection feed
                        </button>
                    </div>

                    <div className="flex items-start gap-[34px] mt-10 flex-wrap">
                        {STATS.map((stat, i) => (
                            <Fragment key={stat.label}>
                                {i > 0 && <div className="w-px self-stretch bg-[#E2E0D7]" />}
                                <div>
                                    <div className="font-grotesk font-bold text-[30px] tracking-[-0.02em] text-[#16181B]">
                                        {stat.value}
                                        {stat.unit && (
                                            <span className="text-[16px] text-[#8A8C86]">
                                                {stat.unit}
                                            </span>
                                        )}
                                    </div>
                                    <div className="text-[13px] text-[#76786F] mt-0.5">
                                        {stat.label}
                                    </div>
                                </div>
                            </Fragment>
                        ))}
                    </div>
                </div>

                {/* Right column — camera mock */}
                <CameraFeedMock />
            </div>
        </section>
    );
}
