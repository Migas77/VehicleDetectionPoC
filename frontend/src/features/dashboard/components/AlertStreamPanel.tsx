import { Link } from '@tanstack/react-router';
import { useMemo } from 'react';

import { ChannelBadge, fmtRel, useNotifications } from '@/features/notifications';

const STREAM_LIMIT = 8;

export function AlertStreamPanel() {
    const { notifications } = useNotifications('all');
    const stream = useMemo(() => notifications.slice(0, STREAM_LIMIT), [notifications]);

    return (
        <div className="bg-white border border-[#EAE8E0] rounded-[18px] flex flex-col flex-1 overflow-hidden min-h-0">
            <div className="px-[18px] pt-4 pb-3 border-b border-[#EFEDE6] flex items-center justify-between">
                <div className="font-grotesk font-semibold text-[16px]">Alert stream</div>
                <Link
                    to="/notifications"
                    className="font-jetbrains text-[11px] text-[#8A8C86] hover:text-[#16181B] transition-colors no-underline"
                >
                    all alerts →
                </Link>
            </div>

            <div className="overflow-y-auto p-2 flex-1 min-h-0">
                {stream.length === 0 ? (
                    <div className="p-10 text-center text-[#9A9C95] text-[13px]">
                        No alerts yet.
                    </div>
                ) : (
                    stream.map((n) => (
                        <div
                            key={n.id}
                            className="flex gap-3 p-3 rounded-xl mb-1.5"
                            style={{ animation: 'vg-up 0.4s ease' }}
                        >
                            <ChannelBadge type={n.type} channel={n.channel} />
                            <div className="flex-1 min-w-0">
                                <div className="font-jetbrains text-[13px] font-semibold text-[#16181B] truncate">
                                    {n.target}
                                </div>
                                <div className="text-[12.5px] text-[#6B6E66] mt-0.5 leading-[1.4] truncate">
                                    {n.desc}
                                </div>
                            </div>
                            <span className="font-jetbrains text-[10.5px] text-[#9A9C95] whitespace-nowrap">
                                {fmtRel(n.ts)}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
