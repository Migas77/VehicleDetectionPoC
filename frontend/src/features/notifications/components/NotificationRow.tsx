import { Check, X } from 'lucide-react';
import { useState } from 'react';
import type { CSSProperties } from 'react';

import type { AlertChannel, Notification, NotificationType } from '../types';

function ChannelBadge({ type, channel }: { type: NotificationType; channel?: AlertChannel }) {
    let bg: string, label: string;

    if (type === 'crash') {
        [bg, label] = ['#E5484D', 'CRASH'];
    } else if (channel === 'sms') {
        [bg, label] = ['#2F9E63', 'SMS'];
    } else {
        [bg, label] = ['#142F32', 'V2X'];
    }

    return (
        <span
            style={{
                display: 'inline-block',
                width: '52px',
                textAlign: 'center',
                padding: '3px 0',
                borderRadius: '6px',
                background: bg,
                color: '#FFFFFF',
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '0.05em',
            }}
        >
            {label}
        </span>
    );
}

function fmtRel(ts: number): string {
    const elapsed = Math.floor((Date.now() - ts) / 1000);
    if (elapsed < 5) return 'just now';
    if (elapsed < 60) return `${elapsed}s ago`;
    const mn = Math.floor(elapsed / 60);
    if (mn < 60) return `${mn}m ago`;
    const h = Math.floor(mn / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function fmtAbs(ts: number): string {
    const d = new Date(ts);
    const mon = MONTHS[d.getMonth()];
    const day = d.getDate();
    const h = String(d.getHours()).padStart(2, '0');
    const m = String(d.getMinutes()).padStart(2, '0');
    const s = String(d.getSeconds()).padStart(2, '0');
    return `${mon} ${day}, ${h}:${m}:${s}`;
}

const MONO: CSSProperties = { fontFamily: "'JetBrains Mono', monospace" };

function CoordsTooltip({
    desc,
    loc,
    coords,
}: {
    desc: string;
    loc: string;
    coords: string | null;
}) {
    const [pos, setPos] = useState<{ x: number; y: number } | null>(null);

    // Only underline when there is a road name distinct from raw coords
    const hasRoadName = coords !== null && loc !== coords;
    const idx = hasRoadName ? desc.indexOf(loc) : -1;

    if (!hasRoadName || idx === -1) {
        return <span style={{ fontSize: '13.5px', color: '#54564F' }}>{desc}</span>;
    }

    const before = desc.slice(0, idx);
    const after = desc.slice(idx + loc.length);

    return (
        <span style={{ fontSize: '13.5px', color: '#54564F' }}>
            {before}
            <span
                style={{
                    borderBottom: '1px dashed rgba(119,124,144,0.45)',
                    cursor: 'default',
                    paddingBottom: '1px',
                }}
                onMouseEnter={(e) => {
                    const r = e.currentTarget.getBoundingClientRect();
                    setPos({ x: r.left, y: r.top });
                }}
                onMouseLeave={() => setPos(null)}
            >
                {loc}
            </span>
            {pos && (
                <div
                    style={{
                        position: 'fixed',
                        top: pos.y - 8,
                        left: pos.x,
                        transform: 'translateY(-100%)',
                        zIndex: 200,
                        background: '#282930',
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: '8px',
                        padding: '6px 10px',
                        boxShadow: '0 4px 16px rgba(0,0,0,0.32)',
                        pointerEvents: 'none',
                    }}
                >
                    <span style={{ ...MONO, fontSize: '11px', color: '#A0A3A8' }}>{coords}</span>
                    <div
                        style={{
                            position: 'absolute',
                            bottom: '-5px',
                            left: '10px',
                            width: '8px',
                            height: '8px',
                            background: '#282930',
                            borderRight: '1px solid rgba(255,255,255,0.08)',
                            borderBottom: '1px solid rgba(255,255,255,0.08)',
                            transform: 'rotate(45deg)',
                        }}
                    />
                </div>
            )}
            {after}
        </span>
    );
}

function CompactTargetCell({
    label,
    details,
}: {
    label: string;
    details: NonNullable<Notification['compactDetails']>;
}) {
    const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
    const { notified, totalInZone } = details;
    const notReached = totalInZone - notified.length;

    return (
        <>
            <span
                style={{
                    ...MONO,
                    fontSize: '13px',
                    fontWeight: 450,
                    color: '#16181B',
                    borderBottom: '1px dashed rgba(119,124,144,0.45)',
                    cursor: 'default',
                    paddingBottom: '1px',
                }}
                onMouseEnter={(e) => {
                    const r = e.currentTarget.getBoundingClientRect();
                    setPos({ x: r.left, y: r.top });
                }}
                onMouseLeave={() => setPos(null)}
            >
                {label}
            </span>
            {pos && (
                <div
                    style={{
                        position: 'fixed',
                        top: pos.y - 10,
                        left: pos.x,
                        transform: 'translateY(-100%)',
                        zIndex: 200,
                        background: '#282930',
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: '10px',
                        padding: '12px 14px',
                        minWidth: '178px',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.36)',
                        pointerEvents: 'none',
                    }}
                >
                    {/* Notified section */}
                    <div
                        style={{
                            ...MONO,
                            fontSize: '10px',
                            fontWeight: 600,
                            letterSpacing: '0.08em',
                            color: '#777C90',
                            textTransform: 'uppercase',
                            marginBottom: '7px',
                        }}
                    >
                        Notified · {notified.length}
                    </div>
                    {notified.map((id) => (
                        <div
                            key={id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '7px',
                                marginBottom: '4px',
                            }}
                        >
                            <Check size={11} color="#2F9E63" strokeWidth={2.5} />
                            <span style={{ ...MONO, fontSize: '12px', color: '#FFFFFF' }}>
                                {id}
                            </span>
                        </div>
                    ))}

                    {/* Not reached section */}
                    {notReached > 0 && (
                        <>
                            <div
                                style={{
                                    height: '1px',
                                    background: 'rgba(255,255,255,0.08)',
                                    margin: '9px 0',
                                }}
                            />
                            <div
                                style={{
                                    ...MONO,
                                    fontSize: '10px',
                                    fontWeight: 600,
                                    letterSpacing: '0.08em',
                                    color: '#777C90',
                                    textTransform: 'uppercase',
                                    marginBottom: '7px',
                                }}
                            >
                                Not reached · {notReached}
                            </div>
                            {Array.from({ length: notReached }).map((_, i) => (
                                <div
                                    key={i}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '7px',
                                        marginBottom: '4px',
                                    }}
                                >
                                    <X size={11} color="#E5484D" strokeWidth={2.5} />
                                    <span style={{ ...MONO, fontSize: '12px', color: '#777C90' }}>
                                        Unknown
                                    </span>
                                </div>
                            ))}
                        </>
                    )}

                    {/* Arrow pointing down toward the target label */}
                    <div
                        style={{
                            position: 'absolute',
                            bottom: '-5px',
                            left: '14px',
                            width: '9px',
                            height: '9px',
                            background: '#282930',
                            borderRight: '1px solid rgba(255,255,255,0.08)',
                            borderBottom: '1px solid rgba(255,255,255,0.08)',
                            transform: 'rotate(45deg)',
                        }}
                    />
                </div>
            )}
        </>
    );
}

interface NotificationRowProps {
    notification: Notification;
    isLast: boolean;
}

export function NotificationRow({ notification, isLast }: NotificationRowProps) {
    const border = isLast ? 'none' : '1px solid #F2F0E9';
    const td: CSSProperties = {
        padding: '12px 20px',
        verticalAlign: 'middle',
        borderBottom: border,
        overflow: 'hidden',
        whiteSpace: 'nowrap',
    };

    return (
        <tr className="hover:bg-[#F9F8F4] transition-colors">
            <td style={td}>
                <ChannelBadge type={notification.type} channel={notification.channel} />
            </td>
            <td style={td}>
                {notification.compactDetails ? (
                    <CompactTargetCell
                        label={notification.target}
                        details={notification.compactDetails}
                    />
                ) : (
                    <span
                        style={{
                            ...MONO,
                            fontSize: '13px',
                            fontWeight: 450,
                            color: '#16181B',
                        }}
                    >
                        {notification.target}
                    </span>
                )}
            </td>
            <td style={{ ...td, textOverflow: 'ellipsis' }}>
                <CoordsTooltip
                    desc={notification.desc}
                    loc={notification.loc}
                    coords={notification.coords}
                />
            </td>
            <td style={td}>
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                        alignItems: 'center',
                        gap: '6px',
                    }}
                >
                    <span style={{ ...MONO, fontSize: '12px', color: '#9A9C95' }}>
                        {fmtAbs(notification.ts)}
                    </span>
                    <span
                        style={{
                            ...MONO,
                            fontSize: '10px',
                            color: '#C0C2BC',
                            minWidth: '48px',
                            textAlign: 'right',
                            flexShrink: 0,
                        }}
                    >
                        {fmtRel(notification.ts)}
                    </span>
                </div>
            </td>
        </tr>
    );
}
