export type NotificationType = 'crash' | 'alert';
export type AlertChannel = 'sms' | 'v2x';
export type PeriodFilter = 'all' | 'live' | 'past';

export interface NotifFilterState {
    crashes: boolean;
    sms: boolean;
    v2x: boolean;
}

export interface Notification {
    id: string;
    incident_id: string;
    type: NotificationType;
    title: string;
    desc: string;
    loc: string;
    target: string;
    ts: number;
    live: boolean;
    channel?: AlertChannel;
    compactDetails?: {
        notified: string[];
        totalInZone: number;
    };
}

export type ViewMode = 'detailed' | 'compact';
