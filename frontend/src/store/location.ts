import { create } from 'zustand';

import type { TrackedEntity, UELocation } from '@/features/map';

const STALE_MS = 15_000;

interface LocationState {
    entities: Record<string, TrackedEntity>;
    updateLocations: (locations: UELocation[]) => void;
}

export const useLocationStore = create<LocationState>()((set) => ({
    entities: {},
    updateLocations: (locations) =>
        set((state) => {
            const now = Date.now();
            const next: Record<string, TrackedEntity> = {};

            for (const [supi, entity] of Object.entries(state.entities)) {
                if (now - entity.lastSeen < STALE_MS) {
                    next[supi] = entity;
                }
            }

            for (const ue of locations) {
                const { area } = ue.location;
                if (area.areaType !== 'CIRCLE') continue;

                next[ue.ue.supi] = {
                    supi: ue.ue.supi,
                    msisdn: ue.ue.msisdn,
                    name: ue.ue.name,
                    lat: area.center.latitude,
                    lng: area.center.longitude,
                    type: ue.type,
                    lastSeen: now,
                };
            }

            return { entities: next };
        }),
}));
