import { useMemo } from 'react';

import { useLocationStore } from '@/store/location';
import { useNotificationsStore } from '@/store/notifications';

import { useMapFiltersStore } from '../store/filters';
import type { TrackedEntity } from '../types';

interface CrashMarker {
    id: string;
    lat: number;
    lng: number;
}

interface MapEntities {
    pedestrians: TrackedEntity[];
    vehicles: TrackedEntity[];
    cameras: TrackedEntity[];
    crashMarkers: CrashMarker[];
    visibleEntities: TrackedEntity[];
}

export function useMapEntities(): MapEntities {
    const entities = useLocationStore((s) => s.entities);
    const wsEvents = useNotificationsStore((s) => s.wsEvents);
    const showPedestrians = useMapFiltersStore((s) => s.showPedestrians);
    const showVehicles = useMapFiltersStore((s) => s.showVehicles);
    const showCameras = useMapFiltersStore((s) => s.showCameras);

    const entityList: TrackedEntity[] = useMemo(() => Object.values(entities), [entities]);

    const pedestrians = useMemo(
        () => entityList.filter((e) => e.type === 'pedestrian'),
        [entityList],
    );
    const vehicles = useMemo(() => entityList.filter((e) => e.type === 'car'), [entityList]);
    const cameras = useMemo(() => entityList.filter((e) => e.type === 'camera'), [entityList]);

    const crashMarkers: CrashMarker[] = useMemo(() => {
        const now = Date.now();
        const TTL = 2 * 60 * 1000;
        const seen = new Map<string, CrashMarker>();
        for (const ev of wsEvents) {
            if (ev.status === 'DETECTED' && ev.location) {
                const age = now - new Date(ev.timestamp).getTime();
                if (age < TTL) {
                    seen.set(ev.incident_id, {
                        id: ev.incident_id,
                        lat: ev.location.latitude,
                        lng: ev.location.longitude,
                    });
                }
            }
        }
        return Array.from(seen.values());
    }, [wsEvents]);

    const visibleEntities: TrackedEntity[] = useMemo(() => {
        const out: TrackedEntity[] = [];
        if (showPedestrians) out.push(...pedestrians);
        if (showVehicles) out.push(...vehicles);
        if (showCameras) out.push(...cameras);
        return out;
    }, [showPedestrians, showVehicles, showCameras, pedestrians, vehicles, cameras]);

    return { pedestrians, vehicles, cameras, crashMarkers, visibleEntities };
}
