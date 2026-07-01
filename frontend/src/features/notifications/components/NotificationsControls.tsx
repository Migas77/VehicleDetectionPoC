import { Check, Filter, RotateCcw, Search, X } from 'lucide-react';
import { useLayoutEffect, useRef, useState } from 'react';

import type { NotifFilterState, PeriodFilter, ViewMode } from '../types';

const PERIOD_TABS: { key: PeriodFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'live', label: 'Live' },
    { key: 'past', label: 'Past' },
];

const VIEW_TABS: { key: ViewMode; label: string }[] = [
    { key: 'detailed', label: 'Detailed' },
    { key: 'compact', label: 'Compact' },
];

const FILTER_ITEMS: { key: keyof NotifFilterState; label: string; dot: string }[] = [
    { key: 'crashes', label: 'Crashes', dot: '#E5484D' },
    { key: 'sms', label: 'SMS Alerts', dot: '#2F9E63' },
    { key: 'v2x', label: 'V2X Alerts', dot: '#142F32' },
];

const CTRL_HEIGHT = 40;

interface NotificationsControlsProps {
    period: PeriodFilter;
    filter: NotifFilterState;
    search: string;
    view: ViewMode;
    onPeriodChange: (p: PeriodFilter) => void;
    onFilterChange: (f: NotifFilterState) => void;
    onSearchChange: (q: string) => void;
    onViewChange: (v: ViewMode) => void;
    onReset: () => void;
}

function SegmentedControl<T extends string>({
    tabs,
    active,
    onChange,
}: {
    tabs: { key: T; label: string }[];
    active: T;
    onChange: (key: T) => void;
}) {
    const btnRefs = useRef<(HTMLButtonElement | null)[]>([]);
    const [pill, setPill] = useState({ left: 0, width: 0, ready: false });

    useLayoutEffect(() => {
        const idx = tabs.findIndex((t) => t.key === active);
        const btn = btnRefs.current[idx];
        if (!btn) return;
        setPill({ left: btn.offsetLeft, width: btn.offsetWidth, ready: true });
    }, [active, tabs]);

    return (
        <div
            style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                height: `${CTRL_HEIGHT}px`,
                boxSizing: 'border-box',
                background: '#FFFFFF',
                border: '1px solid #EAE8E0',
                borderRadius: '11px',
                padding: '4px',
                gap: '2px',
                flexShrink: 0,
            }}
        >
            {pill.ready && (
                <div
                    style={{
                        position: 'absolute',
                        top: '4px',
                        bottom: '4px',
                        left: `${pill.left}px`,
                        width: `${pill.width}px`,
                        borderRadius: '7px',
                        background: '#16181B',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.18)',
                        transition:
                            'left 0.22s cubic-bezier(0.4, 0, 0.2, 1), width 0.22s cubic-bezier(0.4, 0, 0.2, 1)',
                        pointerEvents: 'none',
                    }}
                />
            )}

            {tabs.map((t, i) => (
                <button
                    key={t.key}
                    ref={(el) => {
                        btnRefs.current[i] = el;
                    }}
                    type="button"
                    onClick={() => onChange(t.key)}
                    style={{
                        position: 'relative',
                        zIndex: 1,
                        padding: '6px 14px',
                        borderRadius: '7px',
                        cursor: 'pointer',
                        fontSize: '13.5px',
                        fontWeight: 600,
                        border: 'none',
                        background: 'transparent',
                        color: active === t.key ? '#F4F3EE' : '#5C5E57',
                        transition: 'color 0.22s cubic-bezier(0.4, 0, 0.2, 1)',
                        fontFamily: 'inherit',
                        whiteSpace: 'nowrap',
                        lineHeight: '1',
                    }}
                >
                    {t.label}
                </button>
            ))}
        </div>
    );
}

function FilterDropdown({
    filter,
    onFilterChange,
}: {
    filter: NotifFilterState;
    onFilterChange: (f: NotifFilterState) => void;
}) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    const activeCount = FILTER_ITEMS.filter((item) => filter[item.key]).length;
    const allActive = activeCount === FILTER_ITEMS.length;
    const noneActive = activeCount === 0;

    const toggle = (key: keyof NotifFilterState) =>
        onFilterChange({ ...filter, [key]: !filter[key] });

    const selectAll = () => onFilterChange({ crashes: true, sms: true, v2x: true });

    const clearAll = () => onFilterChange({ crashes: false, sms: false, v2x: false });

    useLayoutEffect(() => {
        if (!open) return;
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, [open]);

    const badgeColor = noneActive ? '#E5484D' : '#E4FB52';
    const badgeText = noneActive ? '#E5484D' : '#16181B';

    return (
        <div ref={ref} style={{ position: 'relative', flexShrink: 0 }}>
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '7px',
                    height: `${CTRL_HEIGHT}px`,
                    boxSizing: 'border-box',
                    padding: '0 14px',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    background: open ? '#16181B' : '#FFFFFF',
                    border: `1px solid ${open ? '#16181B' : '#EAE8E0'}`,
                    fontSize: '13.5px',
                    fontWeight: 600,
                    color: open ? '#F4F3EE' : '#16181B',
                    fontFamily: 'inherit',
                    whiteSpace: 'nowrap',
                    transition: 'background 0.15s, color 0.15s, border-color 0.15s',
                }}
            >
                <Filter size={14} style={{ flexShrink: 0, opacity: open ? 0.85 : 1 }} />
                Filters
                <span
                    style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minWidth: '18px',
                        height: '18px',
                        borderRadius: '9px',
                        background: open ? 'rgba(255,255,255,0.15)' : badgeColor,
                        color: open ? '#F4F3EE' : badgeText,
                        fontSize: '11px',
                        fontWeight: 700,
                        padding: '0 5px',
                        lineHeight: 1,
                    }}
                >
                    {activeCount}
                </span>
            </button>

            {open && (
                <div
                    style={{
                        position: 'absolute',
                        top: 'calc(100% + 6px)',
                        right: 0,
                        minWidth: '196px',
                        background: '#FFFFFF',
                        border: '1px solid #EAE8E0',
                        borderRadius: '14px',
                        boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 2px 6px rgba(0,0,0,0.06)',
                        zIndex: 50,
                        overflow: 'hidden',
                    }}
                >
                    {/* Header */}
                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '12px 14px 10px',
                        }}
                    >
                        <span
                            style={{
                                fontSize: '11px',
                                fontWeight: 700,
                                letterSpacing: '0.08em',
                                textTransform: 'uppercase',
                                color: '#9A9C95',
                                fontFamily: "'JetBrains Mono', monospace",
                            }}
                        >
                            Show
                        </span>
                        <button
                            type="button"
                            onClick={allActive ? clearAll : selectAll}
                            style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '12.5px',
                                fontWeight: 600,
                                color: '#5C5E57',
                                fontFamily: 'inherit',
                                padding: '2px 6px',
                                borderRadius: '6px',
                                transition: 'background 0.12s, color 0.12s',
                            }}
                            onMouseEnter={(e) => {
                                (e.currentTarget as HTMLButtonElement).style.background = '#F4F3EE';
                                (e.currentTarget as HTMLButtonElement).style.color = '#16181B';
                            }}
                            onMouseLeave={(e) => {
                                (e.currentTarget as HTMLButtonElement).style.background = 'none';
                                (e.currentTarget as HTMLButtonElement).style.color = '#5C5E57';
                            }}
                        >
                            {allActive ? 'Clear all' : 'Select all'}
                        </button>
                    </div>

                    {/* Divider */}
                    <div style={{ height: '1px', background: '#EAE8E0', margin: '0 14px' }} />

                    {/* Checkbox rows */}
                    <div style={{ padding: '6px' }}>
                        {FILTER_ITEMS.map((item) => {
                            const checked = filter[item.key];
                            return (
                                <button
                                    key={item.key}
                                    type="button"
                                    onClick={() => toggle(item.key)}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '10px',
                                        width: '100%',
                                        padding: '10px 10px',
                                        borderRadius: '9px',
                                        cursor: 'pointer',
                                        background: 'transparent',
                                        border: 'none',
                                        fontFamily: 'inherit',
                                        textAlign: 'left',
                                        transition: 'background 0.1s',
                                    }}
                                    onMouseEnter={(e) => {
                                        (e.currentTarget as HTMLButtonElement).style.background =
                                            '#F4F3EE';
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.currentTarget as HTMLButtonElement).style.background =
                                            'transparent';
                                    }}
                                >
                                    {/* Color dot */}
                                    <span
                                        style={{
                                            width: '8px',
                                            height: '8px',
                                            borderRadius: '50%',
                                            background: item.dot,
                                            display: 'block',
                                            flexShrink: 0,
                                        }}
                                    />
                                    {/* Label */}
                                    <span
                                        style={{
                                            flex: 1,
                                            fontSize: '13.5px',
                                            fontWeight: checked ? 600 : 400,
                                            color: '#16181B',
                                            transition: 'font-weight 0.1s',
                                        }}
                                    >
                                        {item.label}
                                    </span>
                                    {/* Custom checkbox */}
                                    <span
                                        style={{
                                            width: '17px',
                                            height: '17px',
                                            borderRadius: '5px',
                                            border: checked ? 'none' : '1.5px solid #C8C6BE',
                                            background: checked ? '#16181B' : 'transparent',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            flexShrink: 0,
                                            transition: 'background 0.15s, border-color 0.15s',
                                        }}
                                    >
                                        {checked && (
                                            <Check size={11} color="#F4F3EE" strokeWidth={2.5} />
                                        )}
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Footer hint */}
                    {noneActive && (
                        <div
                            style={{
                                padding: '8px 14px 12px',
                                fontSize: '12px',
                                color: '#E5484D',
                                fontWeight: 500,
                                textAlign: 'center',
                            }}
                        >
                            No filters active - nothing will show
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function ResetButton({ onReset }: { onReset: () => void }) {
    return (
        <button
            type="button"
            onClick={onReset}
            aria-label="Reset filters and search"
            title="Reset filters and search"
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: `${CTRL_HEIGHT}px`,
                height: `${CTRL_HEIGHT}px`,
                boxSizing: 'border-box',
                borderRadius: '10px',
                cursor: 'pointer',
                background: '#FFFFFF',
                border: '1px solid #EAE8E0',
                color: '#16181B',
                flexShrink: 0,
                transition: 'background 0.15s, border-color 0.15s',
            }}
            onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = '#F4F3EE';
            }}
            onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = '#FFFFFF';
            }}
        >
            <RotateCcw size={15} />
        </button>
    );
}

export function NotificationsControls({
    period,
    filter,
    search,
    view,
    onPeriodChange,
    onFilterChange,
    onSearchChange,
    onViewChange,
    onReset,
}: NotificationsControlsProps) {
    return (
        <div
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
            }}
        >
            <SegmentedControl tabs={PERIOD_TABS} active={period} onChange={onPeriodChange} />
            <SegmentedControl tabs={VIEW_TABS} active={view} onChange={onViewChange} />

            {/* Search - fills remaining width */}
            <div
                style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    height: `${CTRL_HEIGHT}px`,
                    boxSizing: 'border-box',
                    padding: '0 14px 0 10px',
                    borderRadius: '10px',
                    background: '#FFFFFF',
                    border: '1px solid #EAE8E0',
                    minWidth: 0,
                }}
            >
                <Search size={16} color="#B6B4AA" style={{ flexShrink: 0 }} />
                <input
                    value={search}
                    onChange={(e) => onSearchChange(e.target.value)}
                    placeholder="Search alerts, targets, locations..."
                    style={{
                        border: 'none',
                        outline: 'none',
                        background: 'transparent',
                        fontFamily: "'DM Sans', system-ui, sans-serif",
                        fontSize: '13.5px',
                        width: '100%',
                        color: '#16181B',
                        minWidth: 0,
                    }}
                />
                {search.length > 0 && (
                    <button
                        type="button"
                        onClick={() => onSearchChange('')}
                        aria-label="Clear search"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '18px',
                            height: '18px',
                            borderRadius: '50%',
                            border: 'none',
                            background: '#EFEDE6',
                            color: '#5C5E57',
                            cursor: 'pointer',
                            flexShrink: 0,
                            padding: 0,
                        }}
                    >
                        <X size={12} strokeWidth={2.5} />
                    </button>
                )}
            </div>

            {/* Filter dropdown */}
            <FilterDropdown filter={filter} onFilterChange={onFilterChange} />

            {/* Reset filters + search - last */}
            <ResetButton onReset={onReset} />
        </div>
    );
}
