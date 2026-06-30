import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';

import { useNotificationsStore } from '@/store/notifications';
import { eventDedupeKey, fetchCrashEvents, mapEventToNotification } from '../api/crash-status';
import type { CrashStatusEvent, Notification, PeriodFilter } from '../types';

export function useNotifications(period: PeriodFilter): { notifications: Notification[] } {
    const wsEvents = useNotificationsStore((s) => s.wsEvents);

    const { data: httpEvents = [] } = useQuery<CrashStatusEvent[]>({
        queryKey: ['crash-status-events'],
        queryFn: () => fetchCrashEvents({ limit: 200 }),
        refetchInterval: period === 'past' ? 10_000 : false,
    });

    const notifications = useMemo<Notification[]>(() => {
        if (period === 'past') {
            return httpEvents
                .map((e) => mapEventToNotification(e, false))
                .sort((a, b) => b.ts - a.ts);
        }

        if (period === 'live') {
            return wsEvents.map((e) => mapEventToNotification(e, true)).sort((a, b) => b.ts - a.ts);
        }

        // 'all': merge WS + HTTP, deduplicated (WS wins, marked live=true)
        const wsKeys = new Set(wsEvents.map(eventDedupeKey));
        const httpOnly = httpEvents.filter((e) => !wsKeys.has(eventDedupeKey(e)));

        return [
            ...wsEvents.map((e) => mapEventToNotification(e, true)),
            ...httpOnly.map((e) => mapEventToNotification(e, false)),
        ].sort((a, b) => b.ts - a.ts);
    }, [period, wsEvents, httpEvents]);

    return { notifications };
}
