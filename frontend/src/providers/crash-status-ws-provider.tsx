import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

import { WS_BASE_URL } from '@/config';
import type { CrashStatusEvent } from '@/features/notifications';
import { useNotificationsStore } from '@/store/notifications';

interface Props {
    children: ReactNode;
}

export function CrashStatusWsProvider({ children }: Props) {
    const addWsEvent = useNotificationsStore((s) => s.addWsEvent);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        let retryTimer: ReturnType<typeof setTimeout> | null = null;
        let unmounted = false;

        function connect() {
            if (unmounted) return;

            const ws = new WebSocket(`${WS_BASE_URL}/ws/crash-status`);
            wsRef.current = ws;

            ws.onmessage = (e) => {
                try {
                    const event = JSON.parse(e.data as string) as CrashStatusEvent;
                    addWsEvent(event);
                } catch {
                    // ignore malformed frames
                }
            };

            ws.onclose = () => {
                if (!unmounted) {
                    retryTimer = setTimeout(connect, 3_000);
                }
            };

            ws.onerror = () => {
                ws.close();
            };
        }

        connect();

        return () => {
            unmounted = true;
            if (retryTimer != null) clearTimeout(retryTimer);
            wsRef.current?.close();
        };
    }, [addWsEvent]);

    return <>{children}</>;
}
