import type { Notification } from '../types';

export interface IncidentZoneTotals {
    ped: number;
    veh: number;
}

export function toCompact(
    notifications: Notification[],
    zoneTotals: Record<string, IncidentZoneTotals> = {},
): Notification[] {
    // Preserve incident order from the input (caller should sort before passing in)
    const incidentOrder: string[] = [];
    const byIncident = new Map<string, Notification[]>();

    for (const n of notifications) {
        if (!byIncident.has(n.incident_id)) {
            incidentOrder.push(n.incident_id);
            byIncident.set(n.incident_id, []);
        }
        byIncident.get(n.incident_id)!.push(n);
    }

    const rows: Notification[] = [];

    for (const incId of incidentOrder) {
        const group = byIncident.get(incId)!;
        const zone = zoneTotals[incId];

        const crash = group.find((n) => n.type === 'crash');
        if (crash) rows.push(crash);

        const sms = group.filter((n) => n.channel === 'sms');
        if (sms.length > 0) {
            const total = zone?.ped ?? sms.length;
            rows.push({
                ...sms[0],
                target: `${sms.length}/${total} PED`,
                desc: `SMS alert sent to ${sms.length} pedestrian${sms.length !== 1 ? 's' : ''} near ${sms[0].loc}.`,
                compactDetails: { notified: sms.map((n) => n.target), totalInZone: total },
            });
        }

        const v2x = group.filter((n) => n.channel === 'v2x');
        if (v2x.length > 0) {
            rows.push({
                ...v2x[0],
                target: 'VEH-MULTICAST',
                desc: `DENM geo-multicast near ${v2x[0].loc}.`,
                compactDetails: undefined,
            });
        }
    }

    return rows;
}
