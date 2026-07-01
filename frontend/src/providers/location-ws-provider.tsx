import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

import { WS_BASE_URL } from '@/config';
import type { UELocation } from '@/features/map';
import { useLocationStore } from '@/store/location';

interface Props {
    children: ReactNode;
}

export function LocationWsProvider({ children }: Props) {
    const updateLocations = useLocationStore((s) => s.updateLocations);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        let retryTimer: ReturnType<typeof setTimeout> | null = null;
        let unmounted = false;

        function connect() {
            if (unmounted) return;

            const ws = new WebSocket(`${WS_BASE_URL}/ws/location`);
            wsRef.current = ws;

            ws.onmessage = (e) => {
                try {
                    const locations = JSON.parse(e.data as string) as UELocation[];
                    updateLocations(locations);
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
    }, [updateLocations]);

    return <>{children}</>;
}
