import { ArrowDown, ArrowUp, ArrowUpDown, ChevronsUp } from 'lucide-react';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';

import { LandingNav } from '@/features/landing';
import {
    NotificationRow,
    NotificationsControls,
    toCompact,
    useNotifications,
    type Notification,
    type NotifFilterState,
    type PeriodFilter,
    type ViewMode,
} from '@/features/notifications';
import { useNotificationsStore } from '@/store/notifications';

const ALL: NotifFilterState = { crashes: true, sms: true, v2x: true };

type SortMode = 'default' | 'time' | 'channel' | 'message' | 'target';

function applySort(rows: Notification[], mode: SortMode): Notification[] {
    if (mode === 'default') return rows;

    if (mode === 'time') return [...rows].reverse();

    if (mode === 'channel') {
        const rank = (n: Notification) => (n.type === 'crash' ? 0 : n.channel === 'sms' ? 1 : 2);
        return [...rows].sort((a, b) => rank(a) - rank(b));
    }

    if (mode === 'message') {
        return [...rows].sort((a, b) => a.desc.localeCompare(b.desc));
    }

    // target
    const idxMap = new Map(rows.map((n, i) => [n.id, i]));
    const firstSeen = new Map<string, number>();
    rows.forEach((n, i) => {
        if (!firstSeen.has(n.target)) firstSeen.set(n.target, i);
    });
    return [...rows].sort((a, b) => {
        const ag = firstSeen.get(a.target) ?? 0;
        const bg = firstSeen.get(b.target) ?? 0;
        if (ag !== bg) return ag - bg;
        return (idxMap.get(a.id) ?? 0) - (idxMap.get(b.id) ?? 0);
    });
}

const TH_BASE: CSSProperties = {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '11px',
    fontWeight: 600,
    letterSpacing: '0.08em',
    textAlign: 'left',
    padding: '12px 20px',
    textTransform: 'uppercase',
    whiteSpace: 'nowrap',
    borderBottom: '1px solid #EAE8E0',
    userSelect: 'none',
    transition: 'color 0.15s',
    position: 'sticky',
    top: 0,
    background: '#FFFFFF',
    zIndex: 10,
};

export function NotificationsPage() {
    const [period, setPeriod] = useState<PeriodFilter>('all');
    const [filter, setFilter] = useState<NotifFilterState>(ALL);
    const [search, setSearch] = useState('');
    const [view, setView] = useState<ViewMode>('detailed');
    const [sort, setSort] = useState<SortMode>('default');

    const setViewingLive = useNotificationsStore((s) => s.setViewingLive);
    const scrollRef = useRef<HTMLDivElement>(null);
    const prevScrollHeightRef = useRef<number>(0);
    const [showScrollTop, setShowScrollTop] = useState(false);

    // Badge should not grow when viewing live data on this page
    useEffect(() => {
        const isViewingLive = period !== 'past';
        setViewingLive(isViewingLive);
        return () => setViewingLive(false);
    }, [period, setViewingLive]);

    const { notifications } = useNotifications(period);

    const handlePeriodChange = (p: PeriodFilter) => {
        setPeriod(p);
        setSort('default');
    };

    const handleViewChange = (v: ViewMode) => {
        setView(v);
    };

    const handleReset = () => {
        setFilter(ALL);
        setSearch('');
    };

    const handleSort = (col: SortMode) => {
        setSort((prev) => (prev === col ? 'default' : col));
    };

    const filtered = notifications.filter((n) => {
        if (n.type === 'crash' && !filter.crashes) return false;
        if (n.type === 'alert' && n.channel === 'sms' && !filter.sms) return false;
        if (n.type === 'alert' && n.channel === 'v2x' && !filter.v2x) return false;
        if (search) {
            const q = search.toLowerCase();
            if (!`${n.title} ${n.desc} ${n.loc} ${n.target}`.toLowerCase().includes(q))
                return false;
        }
        return true;
    });

    const displayed =
        view === 'compact' ? applySort(toCompact(filtered, {}), sort) : applySort(filtered, sort);

    const liveCount = notifications.filter((n) => n.live).length;
    const countLabel = `${notifications.length} total · ${liveCount} live this session`;

    const hasContent = displayed.length > 0;

    // Show scroll-to-top button while the user has scrolled down
    useEffect(() => {
        const el = scrollRef.current;
        if (!el) return;
        const onScroll = () => setShowScrollTop(el.scrollTop > 0);
        el.addEventListener('scroll', onScroll, { passive: true });
        return () => el.removeEventListener('scroll', onScroll);
    }, [hasContent]);

    // Reset anchor whenever filters, sort, or view change so scroll returns to top
    useLayoutEffect(() => {
        prevScrollHeightRef.current = 0;
        setShowScrollTop(false);
        if (scrollRef.current) scrollRef.current.scrollTop = 0;
    }, [sort, filter, search, period, view]);

    // When new items are prepended (live websocket), keep user's visual position fixed
    useLayoutEffect(() => {
        const el = scrollRef.current;
        if (!el) return;

        const prevHeight = prevScrollHeightRef.current;
        if (prevHeight > 0 && el.scrollTop > 0) {
            const diff = el.scrollHeight - prevHeight;
            if (diff > 0) el.scrollTop = el.scrollTop + diff;
        }

        prevScrollHeightRef.current = el.scrollHeight;
    }, [displayed]);

    const thStyle = (col: SortMode): CSSProperties => ({
        ...TH_BASE,
        color: sort === col ? '#16181B' : '#777C90',
        cursor: 'pointer',
    });

    const iconStyle: CSSProperties = {
        display: 'inline-block',
        verticalAlign: 'middle',
        marginLeft: '4px',
        flexShrink: 0,
    };

    const sortIcon = (col: SortMode) => {
        if (sort === col) return <ArrowUp size={11} style={iconStyle} />;
        if (col === 'time') return <ArrowDown size={11} style={iconStyle} />;
        return <ArrowUpDown size={11} style={iconStyle} />;
    };

    return (
        <div
            className="font-dm"
            style={{
                height: '100vh',
                overflow: 'hidden',
                background: '#F4F3EE',
                color: '#16181B',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            <LandingNav />
            <main
                className="pt-20"
                style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
            >
                <div
                    style={{
                        maxWidth: '1480px',
                        width: '100%',
                        margin: '0 auto',
                        padding: '22px 24px 0',
                        flex: 1,
                        overflow: 'hidden',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '16px',
                    }}
                >
                    {/* Header */}
                    <div>
                        <h2
                            style={{
                                fontFamily: "'Space Grotesk', system-ui, sans-serif",
                                fontWeight: 700,
                                fontSize: '26px',
                                letterSpacing: '-0.02em',
                                margin: 0,
                            }}
                        >
                            Notifications
                        </h2>
                        <div
                            style={{
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: '12px',
                                color: '#8A8C86',
                                marginTop: '4px',
                            }}
                        >
                            {countLabel}
                        </div>
                    </div>

                    {/* Controls */}
                    <NotificationsControls
                        period={period}
                        filter={filter}
                        search={search}
                        view={view}
                        onPeriodChange={handlePeriodChange}
                        onFilterChange={setFilter}
                        onSearchChange={setSearch}
                        onViewChange={handleViewChange}
                        onReset={handleReset}
                    />

                    {/* Transparent flex:1 wrapper: lets the white box shrink to content
                         while max-height:100% caps it at the remaining viewport space */}
                    <div
                        style={{
                            flex: 1,
                            minHeight: 0,
                            overflow: 'hidden',
                            paddingBottom: '24px',
                            position: 'relative',
                        }}
                    >
                        <div
                            style={{
                                maxHeight: '100%',
                                overflow: 'hidden',
                                background: '#FFFFFF',
                                border: '1px solid #EAE8E0',
                                borderRadius: '18px',
                                display: 'flex',
                                flexDirection: 'column',
                            }}
                        >
                            {displayed.length === 0 ? (
                                <div
                                    style={{
                                        padding: '60px',
                                        textAlign: 'center',
                                        color: '#9A9C95',
                                        fontSize: '14.5px',
                                    }}
                                >
                                    No notifications match these filters.
                                </div>
                            ) : (
                                <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto' }}>
                                    <table
                                        style={{
                                            width: '100%',
                                            borderCollapse: 'collapse',
                                            tableLayout: 'fixed',
                                        }}
                                    >
                                        <colgroup>
                                            <col style={{ width: '90px' }} />
                                            <col style={{ width: '210px' }} />
                                            <col style={{ width: '340px' }} />
                                            <col style={{ width: '210px' }} />
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th
                                                    style={thStyle('channel')}
                                                    onClick={() => handleSort('channel')}
                                                >
                                                    Channel{sortIcon('channel')}
                                                </th>
                                                <th
                                                    style={thStyle('target')}
                                                    onClick={() => handleSort('target')}
                                                >
                                                    Target{sortIcon('target')}
                                                </th>
                                                <th
                                                    style={thStyle('message')}
                                                    onClick={() => handleSort('message')}
                                                >
                                                    Message{sortIcon('message')}
                                                </th>
                                                <th
                                                    style={thStyle('time')}
                                                    onClick={() => handleSort('time')}
                                                >
                                                    <div
                                                        style={{
                                                            display: 'flex',
                                                            justifyContent: 'flex-end',
                                                            alignItems: 'center',
                                                        }}
                                                    >
                                                        Time{sortIcon('time')}
                                                    </div>
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {displayed.map((n, i) => (
                                                <NotificationRow
                                                    key={n.id}
                                                    notification={n}
                                                    isLast={i === displayed.length - 1}
                                                />
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>

                        <button
                            onClick={() => {
                                scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
                            }}
                            aria-label="Scroll to top"
                            style={{
                                position: 'absolute',
                                bottom: '32px',
                                right: '12px',
                                width: '44px',
                                height: '44px',
                                borderRadius: '50%',
                                border: 'none',
                                background: '#16181B',
                                color: '#E4FB52',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                boxShadow: '0 4px 16px rgba(0,0,0,0.22)',
                                opacity: showScrollTop ? 1 : 0,
                                transform: showScrollTop ? 'translateY(0)' : 'translateY(10px)',
                                pointerEvents: showScrollTop ? 'auto' : 'none',
                                transition: 'opacity 0.22s ease, transform 0.22s ease',
                                zIndex: 50,
                            }}
                        >
                            <ChevronsUp size={20} />
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}
