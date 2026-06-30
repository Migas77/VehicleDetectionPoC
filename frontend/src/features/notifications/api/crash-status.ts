import { API_BASE_URL } from '@/config';
import type { CrashStatusEvent, Notification } from '../types';

export function eventDedupeKey(e: CrashStatusEvent): string {
    return `${e.incident_id}::${e.status}::${e.channel ?? ''}::${e.recipient ?? ''}::${e.timestamp}`;
}

function fmtLocation(event: CrashStatusEvent): string {
    const loc = event.location;
    if (!loc) return 'Unknown location';
    return loc.road_name ?? `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`;
}

function fmtCoords(event: CrashStatusEvent): string | null {
    const loc = event.location;
    if (!loc) return null;
    return `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`;
}

export function mapEventToNotification(event: CrashStatusEvent, live: boolean): Notification {
    const loc = fmtLocation(event);
    const coords = fmtCoords(event);
    const ts = new Date(event.timestamp).getTime();

    if (event.status === 'DETECTED') {
        return {
            id: eventDedupeKey(event),
            incident_id: event.incident_id,
            type: 'crash',
            title: 'Collision detected',
            desc: `Crash detected near ${loc}.`,
            loc,
            coords,
            target: `CAM-${event.camera_supi}`,
            ts,
            live,
        };
    }

    if (event.channel === 'SMS') {
        return {
            id: eventDedupeKey(event),
            incident_id: event.incident_id,
            type: 'alert',
            channel: 'sms',
            title: 'Crash alert',
            desc: `SMS alert sent near ${loc}.`,
            loc,
            coords,
            target: `PED-${event.recipient ?? 'UNKNOWN'}`,
            ts,
            live,
        };
    }

    // DENM - geo-multicast (quadtree tiling), no individual vehicle recipient
    return {
        id: eventDedupeKey(event),
        incident_id: event.incident_id,
        type: 'alert',
        channel: 'v2x',
        title: 'DENM hazard broadcast',
        desc: `DENM geo-multicast near ${loc}.`,
        loc,
        coords,
        target: 'VEH-MULTICAST',
        ts,
        live,
    };
}

export async function fetchCrashEvents(params?: {
    limit?: number;
    offset?: number;
}): Promise<CrashStatusEvent[]> {
    const url = new URL(`${API_BASE_URL}/crash-status/events`);
    if (params?.limit != null) url.searchParams.set('limit', String(params.limit));
    if (params?.offset != null) url.searchParams.set('offset', String(params.offset));

    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json() as Promise<CrashStatusEvent[]>;
}
